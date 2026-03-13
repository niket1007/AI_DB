import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Suggest Optimization", page_icon="⚡")

st.title("⚡ AI Optimization Agent")
st.markdown("This agent autonomously monitors native database profiling tables to suggest performance improvements.")

# 1. Select Connection (Assuming you have a way to fetch saved connections)
# For this example, we use a simple input
conn_name = st.text_input("Enter Connection Name (e.g., 'WikiSQL_Postgres')")
conn_url = st.text_input("Database URL", type="password")

if st.button("🚀 Analyze Performance"):
    with st.spinner("Scanning database profiling tables..."):
        try:
            response = requests.post(
                "http://localhost:8001/suggest-optimize",
                json={"connection_url": conn_url}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result["error"]:
                    st.error(f"DB Status: {result['error']}")
                else:
                    st.success(f"Successfully analyzed {result['dialect']} metrics.")
                    
                    # Layout
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("📊 Top Expensive Queries")
                        if result["raw_stats"]:
                            df = pd.DataFrame(result["raw_stats"])
                            st.dataframe(df)
                        else:
                            st.info("No active query stats found for today.")
                            
                    with col2:
                        st.subheader("🤖 AI Suggestions")
                        st.markdown(result["suggestions"])
                        
            else:
                st.error("Failed to connect to backend.")
                
        except Exception as e:
            st.error(f"Error: {e}")

st.info("Note: For PostgreSQL, ensure 'pg_stat_statements' is enabled in your database extensions.")