import streamlit as st
import requests
from decouple import config
import json

# Services
from services.services import get_connection_strings, call_optimize_api

def show_optimize_db_ui_page():
    API_URL = config("so_api_url", cast=str) + "optimize"

    if st.session_state.get("logged_in", False):
        st.header("🛠️ Database Query Optimizer")
        st.write("Analyze recent Text-to-SQL logs to identify bottlenecks and generate optimization strategies.")

        connections = st.session_state.get("connections", None)
        if connections is None or connections == []:
            connections = get_connection_strings()
            st.session_state["connections"] = connections
            if connections is None or connections == []:
                st.warning("No connections saved.")
                return
        
        conn_map = connections
        selected_name = st.selectbox(
            "Select a database to chat with:", 
            [conn[1] for conn in conn_map])

        for conn in conn_map:
            if conn[1] == selected_name:
                selected_connection_string = conn[2]
        
        st.text(f"Selected Connection: {selected_connection_string[:20]}")

        is_clicked = st.button("Generate Optimization Insights", type="primary")

        if is_clicked and selected_connection_string:
            with st.spinner("Running SLM analysis...", show_time=True):
                try:
                    er_diagram = json.loads(conn[-1])
                    insights = call_optimize_api(
                        selected_connection_string, er_diagram)

                    if insights[0] is False:
                        st.error(insights[1])
                        return
                    else:
                        for index, insight in enumerate(insights[-1]["suggestions"]):
                            with st.expander(f"{index}"):
                                st.markdown("**Original Query:**")
                                st.code(insight['query'], language="sql")

                                st.markdown("**SLM Suggestion:**")
                                msg_type = st.info
                                if insight["suggestion"].startswith("ERROR"):
                                    msg_type = st.error
                                msg_type(insight['suggestion'])
                                
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to connect to the optimization API: {e}")
    else:
        st.session_state.page = "login"
        st.rerun()