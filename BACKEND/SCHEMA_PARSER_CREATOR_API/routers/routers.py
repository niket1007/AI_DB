from fastapi import APIRouter
from services.schema_validator import main_validation_func
from models.create_schema_models import RequestPayloadModel
from services.schema_parser import parse_and_create_schema

router = APIRouter()

@router.post("/create-schema")
async def create_schema(payload: RequestPayloadModel):
    data = main_validation_func(payload)
    response = await parse_and_create_schema(data) 
    return response
