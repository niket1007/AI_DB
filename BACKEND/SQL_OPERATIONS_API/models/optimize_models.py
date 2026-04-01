from pydantic import BaseModel, Field
from models.db_schema_model import JSONModel

class RequestPayload(BaseModel):
    connection_url: str = Field(description="DB connection string")
    er_diagram_json: JSONModel = Field(description="DB Schema Infomations")

class DBFailure(BaseModel):
    msg: str = Field(description="Error message")

class SuggestionModel(BaseModel):
    query: str = Field(description="Query")
    suggestion: str = Field(description="Optimizer suggestion")

class SuccessResponse(BaseModel):
    suggestions: list[SuggestionModel] = Field(description="List of suggestions")