import streamlit as st
import time

def show_login_page():
    st.title("Login to AI-DB")
    
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
                registered_users = st.session_state.get("registered_user", [])

                for user in registered_users:
                    if username == user["username"] and password == user["password"]:
                        st.success("Login successful!")
                        st.session_state.logged_in = True
                        
                if not(st.session_state.get("logged_in", False)):
                    if (username == "user" and password == "pass"):
                        st.success("Login successful!")
                        st.session_state.logged_in = True
                
                if st.session_state.get("logged_in", False):
                    st.session_state.user_name = username
                    st.session_state.page = "guide"
                    time.sleep(1)
                    st.rerun()    
                else:
                    st.error("Incorrect username or password")

