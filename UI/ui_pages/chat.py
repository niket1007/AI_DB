import streamlit as st

def show_chat_ui_page():
    if st.session_state.get("logged_in", False):
        st.title("Text to SQL (Module 2)")

        mock_connections = st.session_state.get("connections", {})
        if not mock_connections:
            st.warning("You have no saved connection strings. Please create a schema first.")
            return

        conn_map = mock_connections
        selected_name = st.selectbox("Select a database to chat with:", conn_map.keys())
        selected_conn_string = conn_map[selected_name]
        
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
