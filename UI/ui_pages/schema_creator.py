import streamlit as st
import time
from static.json_related_data import EXAMPLE_JSON_SCHEMA
from static.connection_string_example import CONNECTION_STRING_GUIDE
import requests
import json
from decouple import config

def show_schema_creator_page():
    if st.session_state.get("logged_in", False):
        st.title("Create New Database Schema")

        st.subheader("1. Enter Connection String")
        st.markdown("Provide a connection string to an **empty, existing** database.")
        connection_string = st.text_input("Database Connection String", "sqlite:///ai_db_user.db")

        with st.expander("Click to see connection string examples"):
            st.markdown(CONNECTION_STRING_GUIDE)
        
        st.subheader("2. Define Your Schema")
        json_schema_text = st.text_area("Paste your JSON Schema here", EXAMPLE_JSON_SCHEMA, height=400)
        
        if st.button("Validate and Create Schema"):
            if not connection_string or not json_schema_text:
                st.error("Please provide both a connection string and a JSON schema.")
                return

            try:
                json_payload_dict = json.loads(json_schema_text)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format in text area: {e}")
                return
            
            api_payload = {
                "connection_url": connection_string,
                "er_diagram_json": json_payload_dict
            }

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
                        return

                    result = r.json()

                    for line in result:
                        if line.startswith("Log: "):
                            message = line[5:]
                            log_content += f"- {message}\n"
                            log_container.markdown(log_content)
                        elif "SUCCESS" in line:
                            st.success("Schema created successfully!")
                            st.session_state.last_connection_string = connection_string
                        elif "ERROR" in line:
                            st.error(line)
                            st.error("Schema creation failed. See log for details.")

            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: Failed to connect to the backend API at {url}. Is it running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                
        if st.session_state.get("last_connection_string"):
            st.subheader("3. Save Connection")
            st.markdown("Save this connection to your account to use in the Chat UI.")
            
            with st.form("save_conn_form"):
                conn_name = st.text_input("Connection Name", "My New Database")
                conn_string_to_save = st.text_input("Connection String", st.session_state.last_connection_string, disabled=True)
                save_submitted = st.form_submit_button("Save Connection")
                
                if save_submitted:
                    st.success(f"Connection '{conn_name}' saved!")
                    if "connections" not in st.session_state:
                        st.session_state.connections = {}
                    st.session_state.connections[conn_name] = conn_string_to_save
                    del st.session_state.last_connection_string
                    time.sleep(1)
                    st.rerun()
    else:
        st.session_state.page = "login"
        st.rerun()