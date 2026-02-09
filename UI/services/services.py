import requests
import json
import streamlit as st
from decouple import config
from db.services import DBService

def call_schema_api(connection_string: str, json_payload_dict: dict) -> bool:
    api_payload = {
        "connection_url": connection_string,
        "er_diagram_json": json_payload_dict
    }
    status = False
    
    log_container = st.empty()
    log_content = "### Creation Log\n\n"
    log_container.markdown(log_content)

    try:
        url = config("api_url", cast=str, default="http://127.0.0.1:8000") + "/create-schema"

        with requests.request(
            "POST",url,
            json=api_payload,
            headers={'Content-Type': 'application/json'},timeout=300) as r:

            if r.status_code != 200:
                try:
                    error_data = r.json() 
                    
                    error_string = error_data.get("error", "")
                    if len(error_string) > 0:
                        error_list = error_string.split("\n")
                        errors_markdown = "\n- ".join(error_list)
                        st.error("Schema Validation Failed:")
                        st.markdown(f"```\n- {errors_markdown}\n```")
                    
                    elif 'detail' in error_data:
                        st.error(f"Error {r.status_code}: {error_data['detail']}")
                    else:
                        st.error(f"Error {r.status_code}: {error_data}")
                        
                except json.JSONDecodeError:
                    st.error(f"Error {r.status_code}: {r.text}")
                    return status

            result = r.json()

            for line in result:
                if line.startswith("Log: "):
                    message = line[5:]
                    log_content += f"- {message}\n"
                    log_container.markdown(log_content)
                elif "SUCCESS" in line:
                    st.success("Schema created successfully!")
                    status = True
                elif "ERROR" in line:
                    st.error(line)
                    st.error("Schema creation failed. See log for details.")
                    status = False
        return status
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: Failed to connect to the backend API at {url}. Is it running?")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return False

def save_connection_string(conn_name: str, conn_string: str, schema: str):
    db_service = DBService()
    u_id = st.session_state.get("user_id", None)

    if u_id is None:
        st.session_state.clear()
        return
    
    res = db_service.create_connection_string(u_id, conn_name, conn_string, schema)
    if res[0]:
        st.success(f"Connection '{conn_name}' saved!")
        
        if "connections" not in st.session_state:
            st.session_state["connections"] = []
        print(st.session_state["connections"])
        st.session_state["connections"].append((
            res[1], conn_name, conn_string, schema))

def get_connection_strings() -> list|None:
    db_service = DBService()
    u_id = st.session_state.get("user_id", None)
    
    if u_id is None:
        st.session_state.clear()
        return None
    
    data = db_service.fetch_connection_strings(u_id)
    return data

def check_valid_query(queries: list[str]) -> list[str]:
    checks = []
    for query in queries:
        if query is None or query.strip() == "":
            checks.append("empty")
        elif query.upper().startswith(("SELECT", "INSERT", "UPDATE")):
            checks.append("valid")
        else:
            checks.append("invalid")
    return checks

def call_query_executor_api(connection_string: str, queries: list[str]) -> bool:
    api_payload = {
        "connection_url": connection_string,
        "queries": queries
    }
    status = False

    try:
        url = config("api_url", cast=str, default="http://127.0.0.1:8000") + "/execute-sql"

        with requests.request(
            "POST",url,
            json=api_payload,
            headers={'Content-Type': 'application/json'}) as r:

            if r.status_code == 200:
                results = r.json()
                for result in results:
                        is_error = False
                        if (isinstance(result["result"], str) and 
                            result["result"].startswith("ERROR")):
                            icon = '❌'
                            is_error = True
                        else:
                            icon = '✅'
                        exp =st.expander(result["query"], icon=icon)
                        if is_error:
                            exp.error(result["result"])
                        else:
                            exp.write(result["result"])
                status = True
            else:
                error_data = r.json()
                st.error(error_data)

        return status
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: Failed to connect to the backend API at {url}. Is it running?")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return False