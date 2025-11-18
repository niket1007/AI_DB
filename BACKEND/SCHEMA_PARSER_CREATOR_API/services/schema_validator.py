from models.create_schema_models import RequestPayloadModel
from models.json_model import TableModel, RelationshipModel, IndexModel
from typing import Optional
from Exceptions.custom_exception import CustomException

def request_payload_validator_and_converter(body: dict) -> Optional[RequestPayloadModel]:
    try:
        data = RequestPayloadModel.model_validate(body)
        return data
    except Exception as e:
        raise CustomException(
            type="VALIDATION_FAILURE", 
            message={"error": "Invalid request payload"})
    

def json_table_validator(tables: list[TableModel]) -> list[str]:
    errors = []
    table_names = set()
    
    for table in tables:

        if table.name in table_names:
            errors.append(f"Duplicate Table '{table.name}'.")
        table_names.add(table.name)
        
        primary_keys = {}
        autoincrement_count = 0
        table_column_names = set()
        for column in table.columns:

            if column.name in table_column_names:
                errors.append(f"Table '{table.name}': Duplicate column name '{column.name}'.")
            table_column_names.add(column.name)

            if column.primary_key is True:
                primary_keys[column.name] = column.autoincrement

            if column.size is not None and column.type not in ["VARCHAR", "CHAR"]:
                errors.append(f"Table '{table.name}', Column '{column.name}': Type '{column.type}' must not have a 'size' field.")
            if column.type in ["VARCHAR", "CHAR"] and (column.size is None or column.size <= 0):
                errors.append(f"Table '{table.name}', Column '{column.name}': Type '{column.type}' requires a positive 'size'.")

            if (column.default == "CURRENT_TIMESTAMP" and column.type != "DATETIME"):
                errors.append(f"Table '{table.name}', Column '{column.name}': Default 'CURRENT_TIMESTAMP' can only be used with 'DATETIME' type.")

            if (column.autoincrement is True):
                autoincrement_count += 1
                if column.type != "INTEGER":
                    errors.append(f"Table '{table.name}', Column '{column.name}': 'autoincrement' is only allowed for 'INTEGER' type.")
                if not (column.primary_key is True):
                    errors.append(f"Table '{table.name}', Column '{column.name}': 'autoincrement' requires 'primary_key: true'.")

            if column.primary_key is True:
                if column.nullable is True:
                    errors.append(f"Table '{table.name}', Column '{column.name}': Primary keys cannot be 'nullable: true'.")
                if column.unique is False:
                    errors.append(f"Table '{table.name}', Column '{column.name}': 'unique' cannot be 'false' when 'primary_key' is 'true'.")

        if len(primary_keys) == 0:
            errors.append(f"Table '{table.name}': No primary key defined. At least one column must have 'primary_key: true'.")

        if autoincrement_count > 1:
            errors.append(f"Table '{table.name}': Has more than one 'autoincrement' column. Only one is allowed per table.")
        elif autoincrement_count == 1 and len(primary_keys) > 1:
            errors.append(f"Table '{table.name}': 'autoincrement' columns cannot be part of a composite (multi-column) primary key.")
        
    return errors

def convert_table_model_to_dict(tables: list[TableModel]):
    table_dict = {}

    for table in tables:
        table_dict[table.name] = {"pu_cols": set(), "cols": set(), "n_cols": set()}

        for column in table.columns:
            if (column.primary_key is True) or (column.unique is True):
                table_dict[table.name]["pu_cols"].add(column.name)
            if column.nullable is True:
                table_dict[table.name]["n_cols"].add(column.name)
            table_dict[table.name]["cols"].add(column.name)
    
    return table_dict 
    

def json_relationship_validator(relationships: list[RelationshipModel], transformedTable: dict) -> list[str]:
    errors = []
    
    if not relationships:
        return errors

    for rel in relationships:
        if rel.from_table not in transformedTable:
            errors.append(f"Relationship Error: 'from_table' '{rel.from_table}' not found in schema.")
            continue
            
        if rel.to_table not in transformedTable:
            errors.append(f"Relationship Error: 'to_table' '{rel.to_table}' not found in schema.")
            continue

        from_table_cols = transformedTable[rel.from_table]["cols"]
        from_table_n_cols = transformedTable[rel.from_table]["n_cols"]
        to_table_cols = transformedTable[rel.to_table]["cols"]
        to_table_pu_cols = transformedTable[rel.to_table]["pu_cols"]

        if rel.from_column not in from_table_cols:
            errors.append(f"Relationship Error: 'from_column' '{rel.from_column}' not found in table '{rel.from_table}'.")
        
        if rel.to_column not in to_table_cols:
            errors.append(f"Relationship Error: 'to_column' '{rel.to_column}' not found in table '{rel.to_table}'.")
        elif rel.to_column not in to_table_pu_cols:
            errors.append(f"Relationship Error: Target column '{rel.to_table}.{rel.to_column}' is not a valid target (must be PRIMARY KEY or UNIQUE).")
        
        if rel.on_delete == "SET NULL":
            if rel.from_column not in from_table_n_cols:
                errors.append(
                    f"Validation Error: Relationship on '{rel.from_table}.{rel.from_column}' "
                    f"has 'on_delete: SET NULL' but the column is NOT NULL. "
                    f"You must set 'nullable: true' to use 'ON DELETE SET NULL'."
                )
    
    return errors

def json_index_validator(indexes: list[IndexModel], transformedTable: dict) -> list[str]:
    errors = []
    index_names = set()

    for index in indexes:
        if index.name in index_names:
            errors.append(f"Duplicate Index '{index.name}'.")
        index_names.add(index.name)
        
        if index.table not in transformedTable:
            errors.append(f"Index '{index.name}': Table '{index.table}' is not present.")
            continue
        
        if len(index.columns) == 0:
            errors.append(f"Index '{index.name}': Column is empty.")
        
        if len(set(index.columns)) != len(index.columns):
            errors.append(f"Index '{index.name}': Duplicate column are present.")
        
        for column in index.columns:
            if column not in transformedTable[index.table]["cols"]:
                errors.append(f"Index '{index.name}': Invalid column name '{column}'.")
    return errors

def main_validation_func(req_body: dict):
    data = request_payload_validator_and_converter(req_body)

    # Table and Column Check
    validation_error = json_table_validator(data.er_diagram_json.tables)
    if len(validation_error) > 0:
        raise CustomException(
            type="VALIDATION_FAILURE", 
            message={"error": "\n".join(validation_error)})
    
    table_dict = convert_table_model_to_dict(data.er_diagram_json.tables)

    # Relationship Check
    validation_error = json_relationship_validator(
        relationships=data.er_diagram_json.relationships,
        transformedTable=table_dict)
    if len(validation_error) > 0:
        raise CustomException(
            type="VALIDATION_FAILURE", 
            message={"error": "\n".join(validation_error)})
    
    # Index Check
    validation_error = json_index_validator(
        indexes=data.er_diagram_json.indexes,
        transformedTable=table_dict)
    if len(validation_error) > 0:
        raise CustomException(
            type="VALIDATION_FAILURE", 
            message={"error": "\n".join(validation_error)})
    
    return data
