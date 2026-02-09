import streamlit as st
from static.json_related_data import EXAMPLE_JSON_SCHEMA
from static.connection_string_example import CONNECTION_STRING_GUIDE
import json
from services.services import call_schema_api, save_connection_string

@st.dialog("Save connection string")
def save_connection_string_dialog(connection_string, json_schema_text):
    st.subheader("3. Save Connection")
    st.markdown("Save this connection to your account to use in the Chat UI.")

    conn_name = st.text_input("Connection Name", "My New Database")
    connection_string_to_save = st.text_input("Connection String", connection_string, disabled=True)
    is_clicked = st.button(label="Save Connection")
    if is_clicked: 
        save_connection_string(conn_name, connection_string_to_save, json_schema_text)

def show_schema_creator_page():
    status = False

    if st.session_state.get("logged_in", False):
        st.title("Create New Database Schema")

        st.subheader("1. Enter Connection String")
        st.markdown("Provide a connection string to an **empty, existing** database.")
        connection_string = st.text_input("Database Connection String", "sqlite:///ai_db_user.db")

        with st.expander("Click to see connection string examples"):
            st.markdown(CONNECTION_STRING_GUIDE)
        
        st.subheader("2. Define Your Schema")
        json_schema_text = st.text_area("Paste your JSON Schema here", EXAMPLE_JSON_SCHEMA, height=400)
        
        is_vc_buton_clicked = st.button(label="Validate and Create Schema")

        if is_vc_buton_clicked:
            if not connection_string or not json_schema_text:
                st.error("Please provide both a connection string and a JSON schema.")
                return
            
            try:
                json_payload_dict = json.loads(json_schema_text)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format in text area: {e}")
                return
                    
            status = call_schema_api(connection_string, json_payload_dict)
            if status:
                save_connection_string_dialog(connection_string, json_schema_text)
                
    else:
        st.session_state.page = "login"
        st.rerun()