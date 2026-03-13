from pydantic import BaseModel, Field
from models.db_schema_model import JSONModel
from typing import Any

class RequestModel(BaseModel):
    connection_url: str = Field(description="DB connection string")
    text: str = Field(description="User provided text for which sql query need to be generated.")
    er_diagram_json: JSONModel = Field(description="DB Schema Infomations")


class SuccessResponseModel(BaseModel):
    sql: str = Field(description="Generated sql from text")
    data: Any = Field(description="Data retireved from DB")
    retries: int = Field(description="Tries taken by SLM for generating the query.", le=2)