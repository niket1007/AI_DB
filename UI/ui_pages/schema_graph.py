import streamlit as st
from services.services import get_connection_strings
import json
import graphviz

def show_schema_graph_ui_page():
    if st.session_state.get("logged_in", False):
        st.title("Schema Graph")
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
                selected_db_schema = conn[-1]
        
        st.text(f"Selected database: {selected_name}")

        graph = graphviz.Graph()
        selected_db_schema = json.loads(selected_db_schema)
        for table in selected_db_schema["tables"]:
            graph.node(table["name"])
        
        for rel in selected_db_schema["relationships"]:
            graph.edge(rel["from_table"], rel["to_table"])
        
        _, col2, _ = st.columns(3)
        col2.graphviz_chart(graph)
    else:
        st.session_state.page = "login"
        st.rerun()