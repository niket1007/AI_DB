import requests
import random
import psycopg
from datetime import datetime, timedelta

SCHEMA_API_URL = "http://127.0.0.1:8000/create-schema"


CONNECTION_URL = "postgresql+psycopg://postgres:pgadmin@localhost:5432/module_3_mt_test"
PSYCOPG_CONN_STR = "dbname=module_3_mt_test user=postgres password=pgadmin host=localhost"

MULTI_TABLE_SCHEMA = {
    "tables": [
        {
            "name": "users",
            "description": "Core table storing customer account details and demographics.",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "autoincrement": True, "nullable": False, "description": "Unique internal ID assigned to the user."},
                {"name": "username", "type": "VARCHAR", "size": 100, "description": "Unique chosen username for the user's account."},
                {"name": "country", "type": "VARCHAR", "size": 50, "description": "Country of residence for the user."},
                {"name": "tier", "type": "VARCHAR", "size": 20, "description": "Subscription or account tier (e.g., Free, Premium, Enterprise)."},
                {"name": "signup_date", "type": "DATETIME", "description": "Date and time when the user registered their account."}
            ]
        },
        {
            "name": "orders",
            "description": "Stores e-commerce transaction records linked to specific users.",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "autoincrement": True, "nullable": False, "description": "Unique internal identifier for the order."},
                {"name": "user_id", "type": "INTEGER", "description": "Foreign key linking the order to the purchasing user in the users table."},
                {"name": "amount", "type": "FLOAT", "description": "Total monetary value of the order transaction."},
                {"name": "status", "type": "VARCHAR", "size": 20, "description": "Current fulfillment status of the order (e.g., Pending, Shipped)."},
                {"name": "order_date", "type": "DATETIME", "description": "Exact date and time the order was placed."}
            ]
        }
    ],
    "relationships": [
        {"from_table": "orders", "from_column": "user_id", "to_table": "users", "to_column": "id"}
    ],
    "indexes": []
}

def generate_multi_table_data():
    print("Calling API to build the users and orders schema...")
    response = requests.post(SCHEMA_API_URL, json={
        "connection_url": CONNECTION_URL, 
        "er_diagram_json": MULTI_TABLE_SCHEMA
    })
    
    if response.status_code != 200:
        print(f"Schema creation failed: {response.text}")
        return

    print("Connecting to Postgres for bulk insertion...")
    base_time = datetime.now()
    countries = ["India", "USA", "UK", "Canada", "Australia", "Germany"]
    tiers = ["Free", "Premium", "Enterprise"]
    statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]

    with psycopg.connect(PSYCOPG_CONN_STR) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_stats (
                    id SERIAL PRIMARY KEY, 
                    query_text TEXT,
                    error_message TEXT,
                    execution_time_ms REAL, 
                    row_count INTEGER,
                    success_status BOOLEAN,
                    explain_plan TEXT
                );
            """)

            print("Generating 10 Lakh (1,000,000) Users...")
            user_batch = []
            for i in range(1, 1000001):
                user_batch.append((
                    f"user_{i}",
                    random.choice(countries),
                    random.choice(tiers),
                    base_time - timedelta(days=random.randint(1, 1000))
                ))
                if len(user_batch) == 100000:
                    cursor.executemany(
                        "INSERT INTO users (username, country, tier, signup_date) VALUES (%s, %s, %s, %s)", 
                        user_batch
                    )
                    user_batch.clear()
                    print(f"   -> Inserted {i} users...")

            print("Generating 40 Lakh (4,000,000) Orders...")
            order_batch = []
            for i in range(1, 4000001):
                order_batch.append((
                    random.randint(1, 1000000), # Random user_id
                    round(random.uniform(10.0, 5000.0), 2),
                    random.choice(statuses),
                    base_time - timedelta(days=random.randint(1, 500))
                ))
                if len(order_batch) == 100000:
                    cursor.executemany(
                        "INSERT INTO orders (user_id, amount, status, order_date) VALUES (%s, %s, %s, %s)", 
                        order_batch
                    )
                    order_batch.clear()
                    print(f"   -> Inserted {i} orders...")

        conn.commit()
    print("PostgreSQL database preparation complete. Total: 50 Lakh rows.")

if __name__ == "__main__":
    generate_multi_table_data()