import streamlit as st
from ui_pages.chat import show_chat_ui_page
from ui_pages.login import show_login_page
from ui_pages.register import show_register_page
from ui_pages.json_guide import show_json_guide_page
from ui_pages.schema_creator import show_schema_creator_page

st.set_page_config(page_title="AI-DB", layout="wide")

def main():

    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    st.sidebar.title("AI-DB 🤖")
    
    if st.session_state.logged_in:
        # LOGGED-IN NAVIGATION
        st.sidebar.header(f"Welcome, {st.session_state.get('user_name', 'User')}")
        st.sidebar.markdown("---")
        
        if st.sidebar.button("JSON Guide"):
            st.session_state.page = "guide"
        if st.sidebar.button("Schema Creator"):
            st.session_state.page = "creator"
        if st.sidebar.button("Chat with DB (Module 2)"):
            st.session_state.page = "chat"    
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()    
    else:
        st.sidebar.header("Welcome")
        if st.sidebar.button("Login"):
            st.session_state.page = "login"
        if st.sidebar.button("Register"):
            st.session_state.page = "register"
            
    st.sidebar.markdown("---")
    st.sidebar.info("M.Tech AI Project\n\nName: Niket Jain\nRoll Number: M25AI1117")

            
    # Page Routing
    if st.session_state.page == "login":
        show_login_page()
    elif st.session_state.page == "register":
        show_register_page()
    elif st.session_state.page == "guide" and st.session_state.logged_in:
        show_json_guide_page()
    elif st.session_state.page == "creator" and st.session_state.logged_in:
        show_schema_creator_page()
    elif st.session_state.page == "chat" and st.session_state.logged_in:
        show_chat_ui_page()
    else:
        st.session_state.page = "login"
        st.session_state.logged_in = False
        st.rerun()

main()