from sqlalchemy import create_engine, Connection, text
from models.execute_sql_models import DBFailure, QueryResult

def _run_insert_update_query(conn: Connection, query: str) -> str:
    try:
        conn.execute(text(query))
        conn.commit()
        return f"SUCCESS"
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

def run_sql_queries(db_connection_string: str, queries: list[str]) -> list[QueryResult] | DBFailure:
    result_log: list[QueryResult] = []
    try:
        engine = create_engine(db_connection_string)
        with engine.connect() as conn:
            for query in queries:
                is_insert_update_failed = False
                
                if query.upper().startswith(("INSERT", "UPDATE")):
                    result = _run_insert_update_query(conn, query)
                    if result.startswith("ERROR"):
                        is_insert_update_failed = True
                elif query.upper().startswith("SELECT"):
                    result = _run_select_query(conn, query)
                
                result_log.append(
                    QueryResult(query=query, result=result))

                if is_insert_update_failed:
                    return result_log
        return result_log
    except Exception as e:
        return DBFailure(error=f"ERROR: {str(e)}")