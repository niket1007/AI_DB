import random
import requests
import json
import os

DB_FILE = os.path.abspath("single_table_test.db")
SQL_OPERATIONS_API_URL = "http://127.0.0.1:8001" # Ensure this points to your Module 3/4 port
CONNECTION_URL = f"postgresql+psycopg://postgres:pgadmin@localhost:5432/module_3_st_test"

def generate_unique_queries(target_count=1000):
    """Generates a guaranteed list of strictly unique slow SQL queries."""
    levels = ["INFO", "WARN", "ERROR", "DEBUG", "CRITICAL"]
    endpoints = ["/api/users", "/api/auth", "/text-to-sql", "/execute-sql", "/ping", "/metrics"]
    browsers = ["Mozilla", "Chrome", "Safari", "Edge", "Firefox", "Postman", "Curl"]
    statuses = [200, 201, 400, 401, 403, 500]

    unique_queries = set()

    print(f"⏳ Generating {target_count} unique slow queries...")
    
    while len(unique_queries) < target_count:
        choice = random.randint(1, 5)
        
        if choice == 1:
            # Issue: Missing standard index
            q = f"SELECT * FROM server_logs WHERE log_level = '{random.choice(levels)}' AND response_time_ms > {random.randint(1000, 10000)};"
        
        elif choice == 2:
            # Issue: Composite index / Group By bottleneck
            q = f"SELECT server_id, COUNT(*) FROM server_logs WHERE endpoint = '{random.choice(endpoints)}' AND payload_size > {random.randint(100, 5000)} GROUP BY server_id;"
        
        elif choice == 3:
            # Issue: Leading wildcard (Full table scan)
            q = f"SELECT * FROM server_logs WHERE user_agent = '{random.choice(browsers)}';"
        
        elif choice == 4:
            # Issue: Heavy Aggregation + Filter (Materialized View / Index candidate)
            q = f"SELECT DATE(timestamp), AVG(response_time_ms) FROM server_logs WHERE payload_size > {random.randint(100, 10000)} GROUP BY DATE(timestamp);"
        
        else:
            # Issue: Unindexed point lookups
            ip = f"192.168.1.{random.randint(1, 255)}"
            q = f"SELECT * FROM server_logs WHERE client_ip = '{ip}' AND status_code = {random.choice(statuses)};"

        unique_queries.add(q)

    return list(unique_queries)

def execute_slow_queries_via_api():
    all_queries = generate_unique_queries(1000)

    BATCH_SIZE = 50 
    print(f"Firing queries at /execute-sql endpoint in batches of {BATCH_SIZE}...")

    for i in range(0, len(all_queries), BATCH_SIZE):
        batch = all_queries[i : i + BATCH_SIZE]
        
        payload = {
            "connection_url": CONNECTION_URL,
            "queries": batch
        }

        response = requests.post(f"{SQL_OPERATIONS_API_URL}/execute-sql", json=payload)
        
        if response.status_code == 200:
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = len(all_queries) // BATCH_SIZE
            print(f"Batch {batch_num}/{total_batches} successfully executed.")
        else:
            print(f"API Failed to execute queries on batch: {response.text}")
            exit()
            
    print("All 1000 unique queries executed and logged!")

def run_optimization():
    print("Triggering SLM Optimization (/optimize)...")
    from db_prep import SINGLE_TABLE_SCHEMA
    
    response = requests.post(f"{SQL_OPERATIONS_API_URL}/optimize", json={
        "connection_url": CONNECTION_URL,
        "er_diagram_json": SINGLE_TABLE_SCHEMA
    })
    
    if response.status_code == 200:
        data = response.json()
        with open("single_table_results.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Results saved to single_table_results.json")
    else:
        print(f"Optimization API Failed: {response.text}")

if __name__ == "__main__":
    execute_slow_queries_via_api()
    run_optimization()