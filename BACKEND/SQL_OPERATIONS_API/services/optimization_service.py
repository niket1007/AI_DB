from sqlalchemy import create_engine, text
from decouple import config
import sqlglot
import sqlglot.expressions as exp
import json
from ollama import AsyncClient

# Models
from models.optimize_models import SuggestionModel

class OptimizationService:
    def __init__(self, connection_url: str, schema: dict):
        self.connection_url = connection_url
        self.schema = schema
        self.engine = create_engine(connection_url)
        self.model = config("model", cast=str)
        self.client = AsyncClient()

    def _get_db_dialect(self) -> str:
        url_lower = self.connection_url.lower()
        if "postgresql" in url_lower:
            return "postgres"
        elif "sqlite" in url_lower:
            return "sqlite"
        elif "mysql" in url_lower:
            return "mysql"
        else:
            return "sql"
    
    def _get_prompt(self, db: str, grouped_stat: dict) -> list:
        system_instr = f"""
            You are a Senior {db} Database Optimization Architect.
            Analyze the schema, normalized SQL query, and the "Execution Variations" to identify the bottleneck.

            DIAGNOSTIC HEURISTICS:
            1. Data Skew: If execution time and query plans change drastically based on the 'Values', the database suffers from data skew. Suggest a Partial Index for the slow values.
            2. Bad Plans: If the Plan shows 'Seq Scan' for a highly selective query, suggest a B-Tree Composite Index.

            CRITICAL NEGATIVE CONSTRAINTS:
            - DO NOT explain what the data, log levels, or status codes mean.
            - DO NOT output any text outside of the three required tags below.

            STRICT OUTPUT FORMAT:
            ISSUE: [One clear sentence explaining the database bottleneck]
            TYPE: [Write exactly "SQL" or "STEPS"]
            ACTION: [Provide the SQL command, or the step-by-step instructions. No extra text.]
        """

        variations_text = ""
        for idx, diff in enumerate(grouped_stat["diff"]):
            variations_text += f"Variation {idx + 1}:\n"
            variations_text += f"- Literal Values Used: {diff['values']}\n"
            variations_text += f"- Execution Time: {diff['executiontimems']} ms\n"
            variations_text += f"- Rows Returned: {diff['row_count']}\n"
            variations_text += f"- Query Plan:\n{diff['explain_plan']}\n\n"
        
        user_content = (
            f"### DATABASE SCHEMA:\n{self.schema}\n\n"
            f"### NORMALIZED QUERY:\n{grouped_stat['query']}\n\n"
            f"### EXECUTION VARIATIONS:\n{variations_text}\n"
            f"--- \n"
            f"TASK: Provide the optimization using EXACTLY the ISSUE:, TYPE:, and ACTION: tags."
        )
        
        return [
            {"role": "system", "content": system_instr},
            {"role": "user", "content": user_content}
        ]

    def _normalize_and_group(self, stats: list) -> list:
        grouped = {}
        
        dialect = self._get_db_dialect().lower() 
        
        for stat in stats:
            raw_sql = stat["query_text"]
            extracted_values = []
            
            try:
                parsed_ast = sqlglot.parse_one(raw_sql, read=dialect)
                
                def extract_and_abstract(node):
                    if isinstance(node, exp.Literal):
                        extracted_values.append(node.this) 
                        return exp.Placeholder() 
                    return node
                
                normalized_ast = parsed_ast.transform(extract_and_abstract)
                normalized_sql = normalized_ast.sql(dialect=dialect)
                
            except Exception as e:
                normalized_sql = raw_sql 
                extracted_values = ["PARSE_ERROR"]

            if normalized_sql not in grouped:
                grouped[normalized_sql] = {
                    "query": normalized_sql,
                    "diff": []
                }
            
            grouped[normalized_sql]["diff"].append({
                "executiontimems": round(stat["execution_time_ms"], 2),
                "values": extracted_values,
                "row_count": stat["row_count"],
                "explain_plan": stat.get("explain_plan", "Not Extracted")
            })
        return list(grouped.values())

    def fetch_db_stats(self) -> list|str:
        try:
            engine = create_engine(self.connection_url)
            query = """
                SELECT * from query_stats 
                WHERE success_status = true AND execution_time_ms > 100
                ORDER BY execution_time_ms DESC;
            """
            with engine.connect() as conn:
                result_list = []
                result = conn.execute(statement=text(query))
                for row in result.mappings():
                    result_list.append(dict(row))
            return result_list
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    async def _call_chat_completion(self, messages: list, temp: float = 0.0) -> str|None:
        try:
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temp
                }
            )

            if response and 'message' in response:
                return response['message'].get('content', "")
            return None
        except Exception as e:
            return f"ERROR: {str(e)}"

    async def call_slm(self, stats: list) -> list:
        db = self._get_db_dialect()
        result = []
        
        grouped_stats = self._normalize_and_group(stats)
        
        for group in grouped_stats:
            prompt = self._get_prompt(db, group)
            response = await self._call_chat_completion(prompt, 0.1)

            if response is None or response == "":
                response = "ERROR: SLM failed to generate a suggestion for this query pattern."
            elif response.startswith("ERROR:"):
                response = response
            
            result.append(
                SuggestionModel(
                    query=group["query"], 
                    suggestion=response
                )
            )
            
        return result