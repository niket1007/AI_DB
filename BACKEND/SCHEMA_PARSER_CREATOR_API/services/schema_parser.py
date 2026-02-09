from sqlalchemy import (
    ForeignKeyConstraint, MetaData, Table, Column, Index, 
    create_engine
)
from sqlalchemy import (
    Integer, Float, VARCHAR, CHAR, DateTime, Date, Time, Boolean
)
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from models.json_model import SUPPORTED_DATATYPE, BaseTableColumnModel
from models.create_schema_models import RequestPayloadModel
import asyncio
from typing import Optional

def _get_sql_type(type_name: SUPPORTED_DATATYPE, size: Optional[int] = None):
    if type_name == "VARCHAR": return VARCHAR(size)
    if type_name == "CHAR": return CHAR(size)
    type_map = {
        "INTEGER": Integer, "FLOAT": Float, "DATETIME": DateTime,
        "DATE": Date, "TIME": Time, "BOOLEAN": Boolean,
    }
    return type_map[type_name]

def _get_column_args(col_data: BaseTableColumnModel) -> dict:
    col_kwargs = {
        "primary_key": col_data.primary_key,
        "unique": col_data.unique,
        "nullable": col_data.nullable,
        "autoincrement": col_data.autoincrement
    }

    default_val = col_data.default
    if default_val:
        if default_val.upper() == "CURRENT_TIMESTAMP":
            col_kwargs["server_default"] = func.now()      
        elif col_data.type == "BOOLEAN":
            col_kwargs["server_default"] = "1" if default_val.lower() == "true" else "0"           
        else:
            col_kwargs["server_default"] = default_val
            
    return col_kwargs

async def parse_and_create_schema(data: RequestPayloadModel) -> list[str]:
    schema_data = data.er_diagram_json
    db_connection_string = data.connection_url
    result_log = []
    
    result_log.append("Log: Connecting to database...")
    try:
        engine = create_engine(db_connection_string)
        metadata = MetaData()
        tables = {} # Hold SQLAlchemy Table objects
    except Exception as e:
        result_log.append(f"ERROR: Could not create database engine.\n{str(e)}")
        return result_log

    # Definition Phase
    result_log.append("Log: Preparing table definitions...")
    
    try:
        # Create all Table objects
        for table_data in schema_data.tables:
            table_name = table_data.name
            col_defs = []
            
            for col_data in table_data.columns:
                sql_type = _get_sql_type(col_data.type, col_data.size)
                
                col_kwargs = _get_column_args(col_data)
                
                col_defs.append(Column(
                    col_data.name,
                    sql_type,
                    **col_kwargs
                ))
            
            tables[table_name] = Table(table_name, metadata, *col_defs)
            
            result_log.append(f"Log: Definition for table '{table_name}' prepared.")
            await asyncio.sleep(0.1)

        # Prepare all Foreign Key constraints
        if schema_data.relationships:
            result_log.append("Log: Preparing foreign key definitions...")
            for rel_data in schema_data.relationships:
                from_table = tables[rel_data.from_table]
                fk_constraint = ForeignKeyConstraint(
                    [rel_data.from_column],
                    [f"{rel_data.to_table}.{rel_data.to_column}"],
                    ondelete=rel_data.on_delete
                )
                from_table.append_constraint(fk_constraint)
                result_log.append(f"Log: Definition for relationship '{rel_data.from_table}.{rel_data.from_column} -> {rel_data.to_column}' prepared.")
                await asyncio.sleep(0.1)

        # Prepare all Index objects
        if schema_data.indexes:
            result_log.append("Log: Preparing index definitions...")
            for idx_data in schema_data.indexes:
                table = tables[idx_data.table]
                columns_to_index = [table.c[col_name] for col_name in idx_data.columns]
                Index(idx_data.name, *columns_to_index) 
                result_log.append(f"Log: Definition for index '{idx_data.name}' on table '{idx_data.table}' prepared.")
                await asyncio.sleep(0.1)

    except Exception as e:
        result_log.append(f"ERROR: Failed during definition phase.\n{str(e)}")
        return result_log

    # Execution Phase (Transactional & Async)
    result_log.append("Log: All definitions complete. Starting database transaction...")
    
    def _create_schema_sync():
        try:
            with engine.begin() as connection:
                metadata.create_all(connection)
            return None # Success
        except Exception as e:
            return e # Return the exception

    try:
        result_log.append("Log: Applying schema to database...")
        error = await asyncio.to_thread(_create_schema_sync)
        if error:
            raise error
        result_log.append("SUCCESS: Database schema created and transaction committed successfully.")
    
    except SQLAlchemyError as e:
        result_log.append(f"ERROR: A database error occurred.\n{str(e)}")
        result_log.append("Log: Transaction failed. Rolling back all changes...")
    except Exception as e:
        result_log.append(f"ERROR: An unexpected error occurred during creation.\n{str(e)}")
        result_log.append("Log: Transaction failed. Rolling back all changes...")
    finally:
        # Close all connections
        engine.dispose()
        result_log.append("Log: Database connection closed.")
        return result_log