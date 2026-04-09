import requests
import random
import psycopg
from datetime import datetime, timedelta

SCHEMA_API_URL = "http://127.0.0.1:8000/create-schema"

CONNECTION_URL = "postgresql+psycopg://postgres:pgadmin@localhost:5432/module_3_st_test"
PSYCOPG_CONN_STR = "dbname=module_3_st_test user=postgres password=pgadmin host=localhost"

SINGLE_TABLE_SCHEMA = {
    "tables": [
        {
            "name": "server_logs",
            "description": "This table contain server logs",
            "columns": [
                {
                    "name": "id", 
                    "type": "INTEGER", 
                    "primary_key": True, 
                    "autoincrement": True,
                    "nullable": False,
                    "description": "row unique Id"
                },
                {
                    "name": "server_id", 
                    "type": "VARCHAR", 
                    "size": 50,
                    "description": "Server unqiue id"
                },
                {
                    "name": "log_level", 
                    "type": "VARCHAR", 
                    "size": 20,
                    "description": "log level error warn etc."
                },
                {
                    "name": "endpoint", 
                    "type": "VARCHAR",
                    "size": 200,
                    "description": "Api endpoint called"
                },
                {
                    "name": "response_time_ms", 
                    "type": "INTEGER",
                    "description": "api response time in millisecond"
                },
                {
                    "name": "status_code", 
                    "type": "INTEGER",
                    "description": "api returned status code"
                },
                {
                    "name": "client_ip", 
                    "type": "VARCHAR", 
                    "size": 50,
                    "description": "client ip address"
                },
                {
                    "name": "user_agent", 
                    "type": "VARCHAR", 
                    "size": 255,
                    "description": "user agent"
                },
                {
                    "name": "payload_size", 
                    "type": "INTEGER",
                    "description": "payload size"
                },
                {
                    "name": "timestamp", 
                    "type": "DATETIME",
                    "description": "log timestamp"
                }
            ]
        }
    ],
    "relationships": [],
    "indexes": []
}

def generate_postgres_data():
    print("Calling Module 1 to build the 10-column table in PostgreSQL...")
    response = requests.post(SCHEMA_API_URL, json={
        "connection_url": CONNECTION_URL, 
        "er_diagram_json": SINGLE_TABLE_SCHEMA
    })
    
    if response.status_code != 200:
        print(f"Schema creation failed: {response.text}")
        return

    print("Bulk inserting 50 Lakh rows into PostgreSQL...")
    
    levels = ["INFO", "WARN", "ERROR", "DEBUG", "CRITICAL"]
    endpoints = ["/api/users", "/api/auth", "/text-to-sql", "/execute-sql", "/ping", "/metrics"]

    user_agents = ["Mozilla", "Chrome", "Safari", "Edge", "Firefox", "Postman", "Curl"]
    
    data_batch = []
    base_time = datetime.now()
    
    for i in range(5000000):
        data_batch.append((
            f"srv-{random.randint(1, 50)}",
            random.choice(levels),
            random.choice(endpoints),
            random.randint(10, 5000),
            random.choice([200, 201, 400, 401, 403, 500]),
            f"192.168.1.{random.randint(1, 255)}",
            random.choice(user_agents),
            random.randint(100, 10000),
            (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
        ))

    with psycopg.connect(PSYCOPG_CONN_STR) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_stats (
                    id SERIAL PRIMARY KEY, 
                    query_text TEXT,
                    execution_time_ms REAL, 
                    row_count INTEGER,
                    success_status BOOLEAN,
                    error_message TEXT,
                    explain_plan TEXT
                );
            """)
            
            cursor.executemany("""
                INSERT INTO server_logs (server_id, log_level, endpoint, response_time_ms, status_code, client_ip, user_agent, payload_size, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data_batch)
            
        conn.commit()
    print("PostgreSQL database preparation complete.")

if __name__ == "__main__":
    generate_postgres_data()