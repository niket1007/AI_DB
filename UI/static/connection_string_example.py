CONNECTION_STRING_GUIDE = """
The standard format is:
`dialect+driver://username:password@host:port/database`

---
### 1. PostgreSQL
* **Example:** `postgresql+psycopg2://user:pass@localhost:5432/my_db`
---
### 2. MySQL / MariaDB
* **Example:** `mysql+pymysql://user:pass@localhost:3306/my_db`
---
### 3. SQLite
* **Example (File):** `sqlite:///my_app.db`
* **Example (In-Memory):** `sqlite:///:memory:`
---
### 4. Microsoft SQL Server
* **Example:** `mssql+pyodbc://user:pass@my_server/my_db?driver=ODBC+Driver+17+for+SQL+Server`
"""