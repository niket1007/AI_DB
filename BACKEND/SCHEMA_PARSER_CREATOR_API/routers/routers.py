from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
from services.schema_validator import main_validation_func
from models.create_schema_models import RequestPayloadModel
from services.schema_parser import parse_and_create_schema

router = APIRouter()

@router.post("/create-schema")
async def create_schema(req: Request, _: RequestPayloadModel|None=None):
    payload = await req.json()
    data = main_validation_func(payload)
    response = await parse_and_create_schema(data) 
    return response
