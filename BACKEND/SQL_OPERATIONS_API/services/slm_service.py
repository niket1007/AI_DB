import json
import re
from decouple import config
from huggingface_hub import AsyncInferenceClient
from Exceptions.custom_exception import CustomException
from models.text_to_sql_models import RequestModel
from models.db_schema_model import JSONModel
from services.query_executors import run_text_to_sql_queries

from ollama import AsyncClient

class SLMService:
    def __init__(self):
        self.model_id = "qwen2.5-coder:7b"
        self.client = AsyncClient()

        

    def _clean_sql(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r'```sql', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```', '', text)
        text = text.replace("\n", " ")
        
        prefixes = [
            r"^here is the query:?", 
            r"^sql:?", 
            r"^the query is:?",
            r"^assistant:?"
        ]
        for pattern in prefixes:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            
        return text.strip()

    def _get_db_dialect(self, url: str) -> str:
        url_lower = url.lower()
        if "postgresql" in url_lower: return "PostgreSQL"
        if "sqlite" in url_lower: return "SQLite"
        return "SQL"

    def _build_system_prompt(self, dialect: str) -> str:
        case_op = "LIKE" if dialect == "SQLite" else "ILIKE"
        
        return (
            f"You are a {dialect} Expert. Generate SQL queries following the given rules only:\n"
            "1. FORMAT: Return ONLY the raw SQL string. No explanations, no markdown, no quotes around the query.\n"
            "2. QUOTING: Wrap every table and column name in double quotes (e.g., \"No.\", \"Member\").\n"
            "3. CASING: Use '" + case_op + "' for all string filters. "
            "To handle messy data, always wrap the value in lowercase: e.g., \"Col\" " + case_op + " 'value'.\n"
            "4. NO WILDCARDS: Do NOT use '%' in LIKE clauses unless the user specifically asks for 'starts with' or 'contains'. "
            "Wrong: LIKE '%3%'. Correct: LIKE '3'.\n"
            "5. AGGREGATION: Only use 'DISTINCT' if the question specifically uses the word 'unique' or 'different'. "
            "Otherwise, use standard COUNT/SUM.\n"
            "6. MINIMAL FILTERS: Only include WHERE conditions for columns explicitly mentioned as constraints in the question. "
            "Do not guess or add extra filters for context.\n"
            "7. LITERALS: If a symbol (%, $, .) is in the question, treat it as a literal character in the value string.\n"
            "8. LIMIT: Never add a LIMIT clause unless a specific rank (e.g., 'top 5') is requested."
        )

    def _format_schema_context(self, schema: JSONModel) -> str:
        context = "Database Schema (JSON Format):\n"
        tables_data = [table.model_dump() for table in schema.tables]
        context += json.dumps(tables_data, indent=2)
        
        if schema.relationships:
            context += "\n\nDefined Relationships (Foreign Keys):\n"
            rels = [f"- {r.from_table}.{r.from_column} references {r.to_table}.{r.to_column}" for r in schema.relationships]
            context += "\n".join(rels)
            
        return context

    async def _call_chat_completion(self, messages: list, temp: float = 0.0) -> str|None:
        try:
            response = await self.client.chat(
                model=self.model_id,
                messages=messages,
                options={
                    "temperature": temp,
                    "stop": ["#", ";", "###", "\n\n"]
                }
            )
            if response and 'message' in response:
                return self._clean_sql(response['message'].get('content', ""))
            return None
        except Exception as e:
            return f"ERROR: {str(e)}"
            
        except Exception as e:
            return f"ERROR: Ollama failed. {str(e)}"

    def build_prompt(
            self, schema: JSONModel, connection_url: str, 
            complexity: str, question: str, 
            error_msg: str|None=None, failed_sql: str|None=None) -> list:
        dialect = self._get_db_dialect(connection_url)
        system_instr = self._build_system_prompt(dialect)
        schema_context = self._format_schema_context(schema)

        if error_msg is None:
            user_content = (
                f"### Query Complexity Hint: {complexity}\n"
                f"### {schema_context}\n"
                f"### Question: {question}\n"
                f"Generate the {dialect} query."
            )
        else:
            user_content = (
                f"### {schema_context}\n"
                f"### Question: {question}\n"
                f"### Previous Error: {error_msg}\n"
                f"### Invalid SQL: {failed_sql}\n"
                "Correct the SQL. Use double quotes and ensure case-insensitive matching without unwanted wildcards."
            )

        return [
            {"role": "system", "content": system_instr},
            {"role": "user", "content": user_content}
        ]

    async def call_text_to_sql(
            self, data: RequestModel, complexity: str, testing: bool) -> list:
        retry_count = 0
        error = None
        failed_sql = None
        while retry_count < 2:
            prompt = self.build_prompt(
                question=data.text,
                schema=data.er_diagram_json,
                connection_url=data.connection_url,
                complexity=complexity,
                error_msg=error,
                failed_sql=failed_sql)
            
            sql = await self._call_chat_completion(prompt)
            
            if sql is None:
                raise CustomException(
                    message={"error": "Unable to generate SQL"})
            elif sql.startswith("ERROR:"):
                raise CustomException(
                    message={"error": sql.replace("ERROR: ", "")})

            # if testing:
            #     return [sql, None]
            # else:
            result = run_text_to_sql_queries(data.connection_url, sql)

            if isinstance(result, str) and result.startswith("ERROR:"):
                error = result
                failed_sql = sql
                retry_count += 1
            else:
                return [sql, result, retry_count]

        raise CustomException(
            message={"error": "Retry Exhausted, Unable to generate SQL"})

    async def suggest_optimizations(self, stats_context: str) -> str:
        system_prompt = (
            "You are an Autonomous Database Administrator (DBA) AI. "
            "Your goal is to analyze database performance statistics and suggest technical improvements. "
            "Focus on: 1. Missing Indexes, 2. Query Refactoring, 3. Cache Potential. "
            "Guidelines:\n"
            "- Be technically precise.\n"
            "- If a query structure uses LIKE without wildcards, suggest exact matching or indexes.\n"
            "- If a table is queried frequently without an index on filter columns, suggest a CREATE INDEX command.\n"
            "- Provide suggestions in clear, bulleted Natural Language."
        )
        
        user_prompt = (
            "Here are the top most expensive queries from our database profiling tables:\n"
            f"{stats_context}\n\n"
            "Based on these structures, what specific performance optimizations do you suggest?"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Slightly higher temperature (0.2) for suggestions to allow for broader reasoning
        response = await self._call_chat_completion(messages, temp=0.2)
        return response if response else "No suggestions available at this time."
