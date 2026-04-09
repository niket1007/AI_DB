import random
import requests
import json
import os

DB_FILE = os.path.abspath("multi_table_test.db")
SQL_OPERATIONS_API_URL = "http://127.0.0.1:8001"

CONNECTION_URL = f"postgresql+psycopg://postgres:pgadmin@localhost:5432/module_3_mt_test"

def generate_unique_queries(target_count=1000):
    """Generates a guaranteed list of strictly unique slow multi-table SQL queries."""
    countries = ["India", "USA", "UK", "Canada", "Australia", "Germany"]
    tiers = ["Free", "Premium", "Enterprise"]
    statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]

    unique_queries = set()

    print(f"Generating {target_count} unique slow JOIN queries...")
    
    while len(unique_queries) < target_count:
        choice = random.randint(1, 5)
        
        if choice == 1:
            # Issue: Missing Foreign Key Index + Filter
            q = f"SELECT u.username, o.amount FROM orders o JOIN users u ON o.user_id = u.id WHERE u.country = '{random.choice(countries)}' AND o.status = '{random.choice(statuses)}' AND o.amount > {random.randint(10, 1000)};"
        
        elif choice == 2:
            # Issue: Heavy Aggregation across JOIN
            q = f"SELECT u.tier, SUM(o.amount) as total_revenue FROM users u JOIN orders o ON u.id = o.user_id WHERE o.order_date > '202{random.randint(3,5)}-0{random.randint(1,9)}-01' GROUP BY u.tier HAVING SUM(o.amount) > {random.randint(1000, 10000)};"
        
        elif choice == 3:
            # Issue: Point Lookup across JOIN (Forces nested loop if unindexed)
            q = f"SELECT * FROM orders o JOIN users u ON o.user_id = u.id WHERE u.username = 'user_{random.randint(1, 1000000)}';"
        
        elif choice == 4:
            # Issue: Range Filtering on Large Table with JOIN + Grouping
            q = f"SELECT u.country, COUNT(o.id) FROM orders o JOIN users u ON o.user_id = u.id WHERE o.amount > {random.randint(100, 4900)} GROUP BY u.country;"
        
        else:
            # Issue: Complex Multi-Condition Hash Join candidate
            q = f"SELECT u.id, u.username FROM users u JOIN orders o ON u.id = o.user_id WHERE u.tier = '{random.choice(tiers)}' AND o.amount BETWEEN {random.randint(10, 100)} AND {random.randint(500, 2000)};"

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
            
    print("All 1000 unique JOIN queries executed and logged!")

def run_optimization():
    print("Triggering SLM Optimization (/optimize)...")

    from db_prep import MULTI_TABLE_SCHEMA 
    
    response = requests.post(f"{SQL_OPERATIONS_API_URL}/optimize", json={
        "connection_url": CONNECTION_URL,
        "er_diagram_json": MULTI_TABLE_SCHEMA
    })
    
    if response.status_code == 200:
        data = response.json()
        with open("multi_table_results.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Results saved to multi_table_results.json")
    else:
        print(f"Optimization API Failed: {response.text}")

if __name__ == "__main__":
    execute_slow_queries_via_api()
    # run_optimization()