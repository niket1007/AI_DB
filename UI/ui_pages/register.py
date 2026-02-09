import streamlit as st
import time
from db.services import DBService

def show_register_page():
    st.title("Register for AI-DB")
    
    db_service = DBService()

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("register_form"):
            name = st.text_input("Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if not name or not username or not password:
                    st.error("Please fill out all fields")
                    return
                res = db_service.create_user(username, password)
                if isinstance(res, bool) and res:
                    st.success("Registration successful! Please log in.")
                    st.session_state.page = "login"
                    if st.session_state.get("registered_user", None) is None:
                        st.session_state.registered_user = [{"username": username, "password": password}]
                    else:
                        st.session_state.registered_user.append({"username": username, "password": password})
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res[1])
