from pydantic import BaseModel, Field
from models.db_schema_model import JSONModel

class RequestModel(BaseModel):
    connection_url: str = Field(description="DB connection string")
    text: str = Field(description="User provided text for which sql query need to be generated.")
    er_diagram_json: JSONModel = Field(description="DB Schema Infomations")