from pydantic import BaseModel, Field
from typing import Any


class RequestModel(BaseModel):
    connection_url: str = Field(description="DB connection string")
    queries: list[str] = Field(description="DB Queries")

class QueryResult(BaseModel):
    query: str = Field(description="DB Query")
    result: Any = Field(description="DB Output")

class DBFailure(BaseModel):
    error: str =Field(
        default="Unable to connect to database.",
        description="DB Connection Error")
