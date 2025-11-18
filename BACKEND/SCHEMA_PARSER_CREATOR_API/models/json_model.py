from pydantic import BaseModel, Field
from typing import Optional, Annotated, Literal, List

SUPPORTED_DATATYPE = Literal["INTEGER", "FLOAT", "VARCHAR", "CHAR", "DATETIME", "DATE", "TIME", "BOOLEAN"]

class BaseTableColumnModel(BaseModel):
    name: Annotated[
        str,
        Field(description="Column Name")]
    type: Annotated[
        SUPPORTED_DATATYPE, # type: ignore
        Field(description="Column Datatype")]
    size: Annotated[
        Optional[int],
        Field(default=None, description="Valid only with VARCHAR and CHAR type")]
    primary_key: Annotated[
        Optional[bool],
        Field(default=None, description="Is column primary key")]
    unique: Annotated[
        Optional[bool],
        Field(default=None, description="Is column unique")]
    nullable: Annotated[
        Optional[bool],
        Field(default=True, description="Is column nullable")]
    default: Annotated[
        Optional[str],
        Field(default=None, description="Column default value")]
    autoincrement: Annotated[
        Optional[bool],
        Field(default=None, description="is column integer and value will be autoincremented")]

class TableModel(BaseModel):
    name: Annotated[
        str,
        Field(description="Table Name")]
    columns: Annotated[
        List[BaseTableColumnModel],
        Field(description="Table Columns Information")]

class RelationshipModel(BaseModel):
    from_table: Annotated[
        str,
        Field(description="Child Table name")]
    from_column: Annotated[
        str,
        Field(description="Child Table column name")]
    to_table: Annotated[
        str,
        Field(description="Parent Table name")]
    to_column: Annotated[
        str,
        Field(description="Parent Table column name")]
    on_delete:  Annotated[
        Optional[Literal["CASCADE", "SET NULL", "NO ACTION", "RESTRICT"]],
        Field(default=None, description="Action to be performed on child table when parent table row is deleted")]

class IndexModel(BaseModel):
    name: Annotated[
        str,
        Field(description="Index name")]
    table: Annotated[
        str,
        Field(description="Table for which index is created")]
    columns: Annotated[
        List[str],
        Field(description="Indexes Columns")]

class JSONModel(BaseModel):
    tables: Annotated[
        List[TableModel],
        Field(description="Tables information")]
    relationships: Annotated[
        Optional[List[RelationshipModel]],
        Field(default=None, description="Foreign Keys Information")]
    indexes: Annotated[
        Optional[List[IndexModel]],
        Field(default=None, description="Indexes Information")]