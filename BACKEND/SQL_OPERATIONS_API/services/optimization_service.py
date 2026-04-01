from sqlalchemy import create_engine, text
from decouple import config
from ollama import AsyncClient

# Exception
from Exceptions.custom_exception import CustomException

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
        if "postgresql" in url_lower: return "PostgreSQL"
        if "sqlite" in url_lower: return "SQLite"
        return "SQL"

    def _get_prompt(self, db: str, stat: dict) -> list:
        
        system_instr = f"""
           You are a {db} database optimization expert.
            Analyze the provided schema, the original query, and the execution stats to identify the primary performance bottleneck. 

            Your task is to provide exactly ONE highly actionable, advanced optimization recommendation. Do not limit yourself to basic indexing. 

            Consider advanced techniques such as:
            - Query Rewriting: (e.g., replacing correlated subqueries with JOINs, optimizing CTEs, eliminating redundant aggregations)
            - Schema Architecture: (e.g., table partitioning, materialized views, denormalization strategies)
            - Advanced Indexing: (e.g., partial indexes, covering indexes, or composite indexes)

            STRICT OUTPUT RULES:
            1. Length Limit: Your response MUST be exactly one paragraph, no more than 3 sentences, and strictly under 50 words.
            2. Structure: Explicitly state the bottleneck, the exact technical fix, and the expected performance benefit.
            3. Negative Constraints: Do NOT provide multiple options. Do NOT include greetings, preamble, or explanations of what the original query does. Return ONLY the recommendation.
        """
        
        user_content = (
                f"### {self.schema}\n"
                f"### Original Query:: {stat["query_text"]}\n"
                f"### Execution Time: {stat["execution_time_ms"]} ms\n"
                f"### Rows Returned: {stat["row_count"]}\n"
            )
        
        return [
            {"role": "system", "content": system_instr},
            {"role": "user", "content": user_content}]

    def fetch_db_stats(self) -> list|str:
        try:
            engine = create_engine(self.connection_url)
            query = """
                SELECT * from query_stats WHERE is_opti_agent_run = false ORDER BY execution_time_ms DESC;
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
            
        except Exception as e:
            return f"ERROR: Ollama failed. {str(e)}"

    async def call_slm(self, stats: list) -> list:
        db = self._get_db_dialect()
        result = []
        for stat in stats:
            if stat["success_status"]:
                prompt = self._get_prompt(db, stat)
                response = await self._call_chat_completion(prompt, 0.1)
                print(response)
                if response is None or response == "":
                    raise CustomException(
                        message={"error": "Unable to generate SQL"})
                elif response.startswith("ERROR:"):
                    raise CustomException(
                        message={"error": response.replace("ERROR: ", "")})
                
                result.append(
                    SuggestionModel(
                        query=stat["query_text"], suggestion=response))
        return result
        