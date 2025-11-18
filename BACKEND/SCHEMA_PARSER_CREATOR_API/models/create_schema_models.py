from pydantic import BaseModel, Field
from models.json_model import JSONModel

class RequestPayloadModel(BaseModel):
    connection_url: str = Field(description="DB connection string")
    er_diagram_json: JSONModel = Field(description="DB Infomations")