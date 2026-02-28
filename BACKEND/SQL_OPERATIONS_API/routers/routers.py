from fastapi import APIRouter, Query
from services.query_executors import run_sql_queries
from models import execute_sql_models, text_to_sql_models
from services.complexity_classifier import Complexity_Classifier
from services.slm_service import SLMService
router = APIRouter()

@router.post("/text-to-sql", tags=["Text to SQL"])
async def create_schema(
    payload: text_to_sql_models.RequestModel,
    testing: bool = Query(default=False, description="Testing mode")):
    cc = Complexity_Classifier(payload.er_diagram_json, payload.text)
    complexity = cc()

    slm = SLMService()
    sql, data = await slm(
        data=payload, complexity=complexity, testing=testing)

    print("API Success Response", sql)
    return {"sql": sql, "data": data}

@router.post("/execute-sql", tags=["Execute SQL"], 
            status_code=200,
            response_model=list[execute_sql_models.QueryResult] | execute_sql_models.DBFailure)
async def execute_sql_endpoint(body: execute_sql_models.RequestModel):
    result = run_sql_queries(body.connection_url, body.queries)
    return result