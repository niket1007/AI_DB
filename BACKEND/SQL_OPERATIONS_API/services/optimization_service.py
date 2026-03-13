import pandas as pd
from sqlalchemy import text, create_engine
from typing import List, Dict, Any
import json

class OptimizationService:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.engine = create_engine(connection_url)
        self.dialect = self.engine.dialect.name

    def fetch_db_stats(self) -> Dict[str, Any]:
        """
        Fetches native profiling data based on the database dialect.
        """
        stats = {"dialect": self.dialect, "data": [], "error": None}
        
        try:
            with self.engine.connect() as conn:
                if self.dialect == "postgresql":
                    # Check if pg_stat_statements is available
                    check_ext = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'")).fetchone()
                    if not check_ext:
                        stats["error"] = "pg_stat_statements extension not enabled. Suggestion: Run 'CREATE EXTENSION pg_stat_statements;'"
                        return stats
                    
                    query = text("""
                        SELECT query, calls, total_exec_time, rows, mean_exec_time
                        FROM pg_stat_statements
                        ORDER BY total_exec_time DESC
                        LIMIT 5;
                    """)
                    
                elif self.dialect == "mysql":
                    query = text("""
                        SELECT DIGEST_TEXT as query, COUNT_STAR as calls, 
                               SUM_TIMER_WAIT/1000000000 as total_exec_time,
                               AVG_TIMER_WAIT/1000000000 as mean_exec_time
                        FROM performance_schema.events_statements_summary_by_digest
                        ORDER BY SUM_TIMER_WAIT DESC
                        LIMIT 5;
                    """)
                
                elif self.dialect == "sqlite":
                    # SQLite fallback: Get schema info to help SLM reason about indexes
                    query = text("SELECT name, sql FROM sqlite_master WHERE type='table';")
                    res = conn.execute(query).fetchall()
                    stats["data"] = [{"table": r[0], "schema": r[1]} for r in res]
                    return stats
                
                else:
                    stats["error"] = f"Profiling not supported for {self.dialect} yet."
                    return stats

                result = conn.execute(query).fetchall()
                stats["data"] = [dict(row._mapping) for row in result]
                
        except Exception as e:
            stats["error"] = str(e)
            
        return stats

    def format_for_slm(self, stats: Dict) -> str:
        """Converts raw DB stats into a readable prompt context."""
        if stats["error"]:
            return f"Database Error or Limitation: {stats['error']}"
        
        context = f"Analyzing {stats['dialect']} performance metrics:\n"
        for i, entry in enumerate(stats["data"]):
            context += f"\nQuery {i+1}: {entry.get('query')}\n"
            context += f"- Calls: {entry.get('calls')}\n"
            context += f"- Total Time: {entry.get('total_exec_time')}ms\n"
            context += f"- Mean Time: {entry.get('mean_exec_time')}ms\n"
            
        return context