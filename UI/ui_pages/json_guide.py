import streamlit as st
from static.json_related_data import EXAMPLE_JSON_SCHEMA, VALIDATION_CHECKS_MARKDOWN

def show_json_guide_page():

    if st.session_state.get("logged_in", False):

        st.header("JSON Schema Guide")
        st.markdown("Your JSON schema must follow a specific structure. It consists of three main keys: `tables`, `relationships`, and `indexes`.")

        st.subheader("Example JSON")
        st.code(EXAMPLE_JSON_SCHEMA, language="json")
        
        st.subheader("Validation Checks")
        st.markdown(VALIDATION_CHECKS_MARKDOWN)
    else:
        st.session_state.page = "login"
        st.rerun()
