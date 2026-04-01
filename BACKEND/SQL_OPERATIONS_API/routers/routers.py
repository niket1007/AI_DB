from fastapi import APIRouter, BackgroundTasks

#Models
from models import execute_sql_models, text_to_sql_models, optimize_models

#Services
from services.query_executors import run_sql_queries
from services.complexity_classifier import Complexity_Classifier
from services.slm_service import SLMService
from services.optimization_service import OptimizationService

router = APIRouter()

@router.post(
        path="/text-to-sql",
        response_model=text_to_sql_models.SuccessResponseModel,
        tags=["Text to SQL"])
async def text_to_sql(
    payload: text_to_sql_models.RequestModel,
    background_tasks: BackgroundTasks):
    cc = Complexity_Classifier(payload.er_diagram_json, payload.text)
    complexity = cc()

    slm = SLMService()
    sql, data, retry_count = await slm.call_text_to_sql(
        data=payload, complexity=complexity, bg_task=background_tasks)

    return text_to_sql_models.SuccessResponseModel(
        sql=sql,
        data=data,
        retries=retry_count
    )

@router.post(
        path="/execute-sql", 
        tags=["Execute SQL"], 
        status_code=200,
        # response_model=list[execute_sql_models.QueryResult] | execute_sql_models.DBFailure
        )
async def execute_sql_endpoint(body: execute_sql_models.RequestModel,
                               background_tasks: BackgroundTasks):
    result = run_sql_queries(body.connection_url, body.queries, background_tasks)
    return result

@router.post(
        path="/optimize",
        response_model=optimize_models.DBFailure | optimize_models.SuccessResponse,
        tags=["Optimize DB"])
async def suggest_optimize(body: optimize_models.RequestPayload):
    opt_service = OptimizationService(
        connection_url=body.connection_url, 
        schema=body.er_diagram_json.model_dump())
    stats = opt_service.fetch_db_stats()
    
    if isinstance(stats, str) and stats.startswith("ERROR"):
        return optimize_models.DBFailure(msg=stats)

    context = await opt_service.call_slm(stats)
    return optimize_models.SuccessResponse(suggestions=context)
    
    