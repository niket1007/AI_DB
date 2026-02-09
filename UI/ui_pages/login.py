import streamlit as st
import time
from db.services import DBService


def show_login_page():
    st.title("Login to AI-DB")
    
    db_service = DBService()

    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password")
                    return
                        
                if not(st.session_state.get("logged_in", False)):
                    res = db_service.check_password(password, username)
                    if res[0]:
                        st.success("Login successful!")
                        st.session_state.logged_in = True
                        st.session_state.user_id = res[1]
            
                if st.session_state.get("logged_in", False):        
                    st.session_state.page = "guide"
                    time.sleep(1)
                    st.rerun()    
                else:
                    st.error("Incorrect username or password")

