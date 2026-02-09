import streamlit as st
from services.services import get_connection_strings, check_valid_query, call_query_executor_api
import pandas as pd
from static.queries_example import QUERIES_EXAMPLE

def show_query_executor_ui_page():
    
    if st.session_state.get("logged_in", False):
        st.title("Query Executor")

        connections = st.session_state.get("connections", None)
        if connections is None:
            connections = get_connection_strings()
            st.session_state["connections"] = connections
            if connections is None:
                st.warning("No connections saved.")
                return
        
        conn_map = connections
        selected_name = st.selectbox(
            "Select a database to chat with:", 
            [conn[1] for conn in conn_map])

        for conn in conn_map:
            if conn[1] == selected_name:
                selected_connection_string = conn[2]
        
        st.text(f"Selected Connection: {selected_connection_string}")

        with st.expander("Click to see supported query examples"):
            st.markdown(QUERIES_EXAMPLE)
        
        df = st.data_editor(
            data=pd.DataFrame(columns=["Query"]), 
            num_rows="dynamic")
        
        is_submitted = st.button("Run queries")

        if is_submitted:
            df_dict = df.to_dict(orient="list")
            result = check_valid_query(df_dict["Query"])

            all_queries_valid = True
            for index, query in enumerate(df_dict["Query"]):
                if result[index] == "invalid":
                    st.warning(f"Invalid SQL Query: {query}")
                    all_queries_valid = False
                elif result[index] == "empty":
                    st.warning(f"Empty sql text provided.")
                    all_queries_valid = False
            
            if all_queries_valid:
                with st.spinner("Running sql queries", show_time=True):
                    call_query_executor_api(selected_connection_string, df_dict["Query"])
    else:
        st.session_state.page = "login"
        st.rerun()