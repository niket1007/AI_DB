from fastapi import BackgroundTasks
import time

from sqlalchemy import create_engine, Connection, text
from models.execute_sql_models import DBFailure, QueryResult

def _get_explain_prefix(url: str) -> str:
        if "sqlite" in url.lower():
            return "EXPLAIN QUERY PLAN "
        return "EXPLAIN "

def _log_query_stat(connection_string: str, query: str,
                    execution_time_ms: float, success_status: bool, 
                    error_msg: str, row_count: int):
    try:
        engine = create_engine(connection_string)
        explain_string = None

        with engine.connect() as conn:
            if (success_status 
                and query.strip().upper().startswith("SELECT")
                and execution_time_ms > 100.0):
                try:
                    explain_prefix = _get_explain_prefix(connection_string)
                    explain_result = conn.execute(text(f"{explain_prefix}{query}"))

                    plan_lines = [str(dict(row)) for row in explain_result.mappings()]
                    explain_string = "\n".join(plan_lines)
                except Exception as e:
                    explain_string = f"Plan extraction failed: {str(e)}"

            stat_query = text("""
                INSERT INTO query_stats (query_text, success_status, execution_time_ms, row_count, error_message, explain_plan)
                VALUES (:query_text, :success_status, :execution_time_ms, :row_count, :error_message, :explain_plan)
            """)
            conn.execute(stat_query, {
                "query_text": query,
                "success_status": success_status,
                "execution_time_ms": round(execution_time_ms, 2),
                "row_count": row_count,
                "error_message": error_msg,
                "explain_plan": explain_string
            })
            conn.commit()
    except Exception as e:
        print(f"Background task failed to log to query_stat table: {str(e)}")

def _log_queries_stat(connection_string: str, stats: list):
    try:
        engine = create_engine(connection_string)
        explain_string = None
        with engine.connect() as conn:
            for stat in stats:
                if (stat["success_status"] 
                    and stat["query_text"].strip().upper().startswith("SELECT")
                    and stat["execution_time_ms"] > 100.0):
                    try:
                        explain_prefix = _get_explain_prefix(connection_string)
                        explain_result = conn.execute(text(f"{explain_prefix}{stat['query_text']}"))

                        plan_lines = [str(dict(row)) for row in explain_result.mappings()]
                        explain_string = "\n".join(plan_lines)
                    except Exception as e:
                        explain_string = f"Plan extraction failed: {str(e)}"
                
                stat["explain_plan"] = explain_string

                stat_query = text("""
                    INSERT INTO query_stats (query_text, success_status, execution_time_ms, row_count, error_message, explain_plan)
                    VALUES (:query_text, :success_status, :execution_time_ms, :row_count, :error_message, :explain_plan)
                """)
                conn.execute(stat_query, stat)
                conn.commit()
    except Exception as e:
        print(f"Background task failed to log to query_stat table: {str(e)}")

def _run_insert_update_query(conn: Connection, query: str) -> str:
    try:
        conn.execute(text(query))
        conn.commit()
        return "SUCCESS"
    except Exception as e:
        conn.rollback()
        return f"ERROR: {str(e)}"

def _run_select_query(conn: Connection, query: str) -> list|str:
    try:
        result_list = []
        result = conn.execute(statement=text(query))
        for row in result.mappings():
            result_list.append(dict(row))
        return result_list
    except Exception as e:
        return f"ERROR: {str(e)}"

def run_sql_queries(
        db_connection_string: str, 
        queries: list[str], bg_task: BackgroundTasks) -> list[QueryResult] | DBFailure:
    result_log: list[QueryResult] = []
    try:
        engine = create_engine(db_connection_string)
        stats = []
        with engine.connect() as conn:
            for query in queries:
                is_insert_update_failed = False
                stat = {"query_text": query}
                start_time = time.perf_counter()

                if query.upper().startswith(("INSERT", "UPDATE")):
                    result = _run_insert_update_query(conn, query)
                    if result.startswith("ERROR"):
                        is_insert_update_failed = True
                elif query.upper().startswith("SELECT"):
                    result = _run_select_query(conn, query)
                
                execution_time_ms = (time.perf_counter() - start_time) * 1000
                stat["execution_time_ms"] = execution_time_ms

                if (isinstance(result, str) and result.startswith("ERROR")):
                    stat["success_status"] = False
                    stat["row_count"] = 0
                    stat["error_message"] = result
                else:
                    stat["success_status"] = True
                    stat["error_message"] = None
                    stat["row_count"] = len(result)

                result_log.append(
                    QueryResult(query=query, result=result))
                stats.append(stat)
                if is_insert_update_failed:
                    bg_task.add_task(
                        _log_queries_stat,
                        db_connection_string, stats)
                    return result_log
        bg_task.add_task(
            _log_queries_stat,
            db_connection_string, stats)
        return result_log
    except Exception as e:
        return DBFailure(error=f"ERROR: {str(e)}")

def run_text_to_sql_queries(
        db_connection_string: str, query: str, bg_task: BackgroundTasks) -> list | str:
    try:
        engine = create_engine(db_connection_string)
        result = []
        with engine.connect() as conn:
            start_time = time.perf_counter()
            row_count = 0

            result = _run_select_query(conn, query)

            execution_time_ms = (time.perf_counter() - start_time) * 1000
            if (isinstance(result, str) and result.startswith("ERROR")):
                success_status = False
                row_count = 0
                error_msg = result
            else:
                success_status = True
                error_msg = None
                row_count = len(result)
            
            bg_task.add_task(
                _log_query_stat,
                db_connection_string,
                query,
                execution_time_ms,
                success_status,
                error_msg,
                row_count
            )
        return result
    except Exception as e:
        return f"ERROR: {str(e)}"