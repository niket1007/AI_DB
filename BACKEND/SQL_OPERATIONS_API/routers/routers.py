from fastapi import APIRouter, Query

#Models
from models import execute_sql_models, text_to_sql_models

#Services
from services.query_executors import run_sql_queries
from services.complexity_classifier import Complexity_Classifier
from services.slm_service import SLMService
from services.optimization_service import OptimizationService

router = APIRouter()

@router.post(
        path="/text-to-sql", 
        responses={
            200: {"models": text_to_sql_models.SuccessResponseModel}
        },
        tags=["Text to SQL"])
async def text_to_sql(
    payload: text_to_sql_models.RequestModel,
    testing: bool = Query(default=False, description="Testing mode")):
    cc = Complexity_Classifier(payload.er_diagram_json, payload.text)
    complexity = cc()

    slm = SLMService()
    sql, data, retry_count = await slm.call_text_to_sql(
        data=payload, complexity=complexity, testing=testing)

    print("API Success Response", sql)
    return {"sql": sql, "data": data, "model_retries": retry_count}

@router.post(
        path="/execute-sql", 
        tags=["Execute SQL"], 
        status_code=200,
        response_model=list[execute_sql_models.QueryResult] | execute_sql_models.DBFailure)
async def execute_sql_endpoint(body: execute_sql_models.RequestModel):
    result = run_sql_queries(body.connection_url, body.queries)
    return result

@router.post(
        path="/suggest-optimize",
        tags=["Optimize DB"])
async def suggest_optimize(data: dict):
    conn_url = data.get("connection_url")
    if not conn_url:
        return {"error": "Connection URL required"}

    # 1. Fetch DB Stats from native tables
    opt_service = OptimizationService(conn_url)
    stats = opt_service.fetch_db_stats()
    
    # 2. Format for AI
    context = opt_service.format_for_slm(stats)
    
    # 3. Call SLM for advice
    suggestions = await SLMService.suggest_optimizations(context)
    
    return {
        "dialect": stats["dialect"],
        "raw_stats": stats["data"],
        "error": stats["error"],
        "suggestions": suggestions
    }