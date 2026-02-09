import streamlit as st
from services.services import get_connection_strings

def show_chat_ui_page():
    if st.session_state.get("logged_in", False):
        st.title("Text to SQL (Module 2)")

        connections = st.session_state.get("connections", None)
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
                selected_conn_string = conn[2]
        
        st.text(f"Connected to: {selected_conn_string[:20]}...")

        st.subheader("Chat with your data")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_chat_db" not in st.session_state or st.session_state.current_chat_db != selected_name:
            st.session_state.messages = []
            st.session_state.current_chat_db = selected_name

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question in plain English (e.g., 'How many users are there?')"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("ai"):
                response = f"""
    This is a **mock response** for the database at `{selected_name}`.

    Module 2 (Text-to-SQL) is not yet implemented.

    Your query was: *"{prompt}"*
                """
                st.markdown(response)
                st.session_state.messages.append({"role": "ai", "content": response})
    else:
        st.session_state.page = "login"
        st.rerun()
