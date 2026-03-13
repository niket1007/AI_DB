import streamlit as st
import json

from services.services import get_connection_strings, call_text_to_sql_api

def show_chat_ui_page():
    if st.session_state.get("logged_in", False):
        st.title("Text to SQL (Module 2)")

        connections = st.session_state.get("connections", None)
        selected_connection = None
        if connections is None:
            print("Inside if")
            connections = get_connection_strings()
            if connections is None:
                st.warning("No connections saved.")
                return

        conn_map = connections
        selected_name = st.selectbox(
            "Select a database to chat with:", 
            [conn[1] for conn in conn_map])
        
        for conn in conn_map:
            if conn[1] == selected_name:
                selected_connection = conn
        
        st.text(f"Connected to: {selected_connection[2][:20]}...")
        st.subheader("Chat with your data")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_chat_db" not in st.session_state or st.session_state.current_chat_db != selected_name:
            st.session_state.messages = []
            st.session_state.current_chat_db = selected_name

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "ai":
                    status, result = message["content"]
                    if status == True:
                        st.markdown("### 🛢️ SQL Query")
                        st.code(result.get("sql"), language="sql")
                        st.markdown("---")
                        st.markdown("### 📊 Data")
                        st.json(result["data"])
                    else:
                        st.markdown("### ❌ Error")
                        st.code(result, language="text")
                else:
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question in plain English (e.g., 'How many users are there?')"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("ai"):
                er_diagram = json.loads(selected_connection[-1])
                with st.spinner("Generating Query and Fetching data from DB........"):
                    status, result = call_text_to_sql_api(selected_connection[2], prompt, er_diagram)
                    if status == True:
                        st.markdown("### 🛢️ SQL Query")
                        st.code(result.get("sql"), language="sql")
                        st.markdown("---")
                        st.markdown("### 📊 Data")
                        st.json(result["data"])
                    else:
                        st.markdown("### ❌ Error")
                        st.code(result, language="text")
                    st.session_state.messages.append({"role": "ai", "content": [status, result]})
    else:
        st.session_state.page = "login"
        st.rerun()
