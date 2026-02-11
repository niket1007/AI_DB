from fastapi import APIRouter, Request
from models.create_schema_models import RequestPayloadModel
from services.query_executors import run_sql_queries
from models import execute_sql_models

router = APIRouter()

@router.post("/text-to-sql", tags=["Text to SQL"])
async def create_schema(payload: RequestPayloadModel|None=None):
    pass

@router.post("/execute-sql", tags=["Execute SQL"], 
            status_code=200,
            response_model=list[execute_sql_models.QueryResult] | execute_sql_models.DBFailure)
async def execute_sql_endpoint(body: execute_sql_models.RequestModel):
    result = run_sql_queries(body.connection_url, body.queries)
    return result