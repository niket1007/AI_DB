# AI-DB: An Intelligent, Self-Optimising SQL Database with a Natural Language Interface

**AI-DB** is a comprehensive, multi-module database management platform designed to democratize data access and automate performance tuning. It bridges the gap between complex SQL operations and non-technical users by utilizing locally hosted Small Language Models (SLMs) to handle everything from database provisioning to natural language querying and autonomous performance optimization.

## 📋 Table of Contents
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Implementation Details](#-implementation-details)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Execution Steps](#-execution-steps)
- [Usage Guide](#-usage-guide)

---

## 🚀 Features

The system is divided into four integrated modules:

### 1. Schema Parser & Creator (Module 1 - Provisioning)
- **JSON-to-SQL Engine:** Define your database schema (tables, columns, relationships, indexes) using a simple, intuitive JSON format.
- **Strict Validation:** The backend rigorously validates the JSON structure before physical creation, checking for duplicate names, valid data types, and ensuring Primary/Foreign Key integrity.
- **Universal Connectivity:** Powered by **SQLAlchemy**, supporting SQLite, PostgreSQL, MySQL, and MSSQL.

### 2. Natural Language Interface (Module 2 - Interaction)
- **Text-to-SQL Chat:** Query your database using plain English. 
- **Decomposed Prompting:** Integrates with local Small Language Models (e.g., Qwen 2.5 Coder, Llama 3.1) to translate complex relational logic into executable SQL.
- **Complexity Classification:** Automatically gauges query complexity to assign appropriate processing resources.

### 3. The AI DBA (Module 3 - Optimization)
- **Autonomic Diagnosis:** An automated background agent that monitors slow queries.
- **Execution Plan Grounding:** Interprets physical database execution plans (e.g., PostgreSQL `EXPLAIN`) to detect structural bottlenecks like massive Sequential Scans or inefficient Hash Joins.
- **Structural Correctives:** Autonomously generates formatted `CREATE INDEX` SQL commands to optimize database performance.

### 4. Unified Dashboard & Execution (Module 4 - Integration)
- **Streamlit Frontend:** A cohesive, responsive web interface for all database operations.
- **Direct SQL Execution:** A dedicated playground to execute raw SQL queries and visualize results.
- **Schema Visualization:** Tools to view and map out the generated database schemas.

---

## 📂 Project Structure

```text
AI_DB/
├── .gitignore
├── README.md
├── requirements.txt                   # Python dependencies
├── BACKEND/
│   ├── SCHEMA_PARSER_CREATOR_API/     # Module 1 Backend
│   │   ├── main.py                    # Entry point for Schema API
│   │   ├── models/                    # Pydantic models for JSON validation
│   │   ├── routers/                   # API endpoints
│   │   └── services/                  # Validation & SQLAlchemy generation
│   └── SQL_OPERATIONS_API/            # Modules 2, 3, and 4 Backend
│       ├── main.py                    # Entry point for SQL Operations API
│       ├── models/                    # Models for Chat, Optimize, and Execute payloads
│       ├── routers/                   # API endpoints for SLM and DB interactions
│       └── services/                  
│           ├── complexity_classifier.py
│           ├── optimization_service.py # AI DBA Logic
│           ├── query_executors.py      # Raw SQL execution
│           └── slm_service.py          # LLM orchestration and prompt building
├── TESTERS/                           # Automated Benchmarking Suites
│   ├── Module_2/                      # Text-to-SQL Evaluators (Spider, WikiSQL)
│   └── Module_3/                      # DBA Performance Stress Tests (Single/Multi-table)
└── UI/
    ├── .env                           # Environment variables
    ├── main.py                        # Entry point for Streamlit Frontend
    ├── db/                            # UI-side SQLite storage (users, saved connections)
    ├── static/                        # Examples and Helper Data
    └── ui_pages/                      # UI Views
        ├── chat.py                    # Natural language query interface
        ├── json_guide.py              # Documentation for Schema Builder
        ├── login.py / register.py     # User Authentication
        ├── optimize_db.py             # AI DBA Dashboard
        ├── query_executor.py          # Raw SQL execution environment
        ├── schema_creator.py          # Module 1 UI
        └── schema_graph.py            # ER Diagram visualizations
```
---

## 🛠 Implementation Details

### Backend Infrastructure (FastAPI)

The backend utilizes two distinct **FastAPI** microservices:

1.  **Schema Creator API:** Focuses entirely on Data Definition Language (DDL). It translates JSON into physical database objects asynchronously.
2.  **SQL Operations API:** Acts as the cognitive engine. It orchestrates connections to local language models (via Ollama) to translate text to SQL, parse Abstract Syntax Trees (AST) using sqlglot, read physical execution plans, and run Data Manipulation Language (DML) queries.

### Frontend (Streamlit)

The frontend utilizes **Streamlit** for rapid UI development:

1.  **State Management:** Uses st.session_state to handle login sessions and persistent database connections across different pages.
2.  **Dynamic Interfaces:** Seamlessly switches between the Schema Creator, SQL Playground, and Chat interfaces using Streamlit's multi-page capabilities.

-----

## 📋 Prerequisites

  * **Python 3.10+** (Project developed on 3.12)
  * **Pip** (Python Package Manager)
  * **Ollama** (Required locally to run the Small Language Models for Text-to-SQL and Optimization features)

-----

## ⚙️ Installation & Setup

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/niket1007/AI_DB.git
    cd AI_DB
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

-----

## ▶️ Execution Steps

This project requires running **two** separate terminals: one for the Backend API and one for the Frontend UI.

### Terminal 1: Backend API

Navigate to the API directory and start the Uvicorn server.
1.
  ```bash
  # From the root AI_DB folder
  cd BACKEND/SCHEMA_PARSER_CREATOR_API
  
  # Run the server
  fastapi dev .\main.py
  ```
  
  You should see: 
  - `API running on http://127.0.0.1:8000`
  - `OpenAPI doc server running on http://127.0.0.1:8000/docs`

2.
  ```bash
  # From the root AI_DB folder
  cd BACKEND/SQL_OPERATIONS_API
  
  # Run the server
  fastapi dev .\main.py --port 8001
  ```
  
  You should see: 
  - `API running on http://127.0.0.1:8001`
  - `OpenAPI doc server running on http://127.0.0.1:8001/docs`


### Terminal 2: Frontend UI

Navigate to the UI directory and start Streamlit.

```bash
# From the root AI_DB folder
cd UI

# Run the UI
streamlit run main.py
```

*This will automatically open your browser to `http://localhost:8501`.*

-----

## 📖 Usage Guide

1.  **Login/Register:**

      - Open the UI.
      - Click **Register** to create a account (e.g., Username: `user`, Password: `pass`).
      - **Login** with those credentials.

2.  **Provision a Database (Module 1)**

      - Navigate to **Schema Creator** from the sidebar.
      - **Connection String:** Enter a valid SQLAlchemy connection string.
          - *For testing, use SQLite:* `sqlite:///test_db.db` (This creates a file named `test_db.db` in the backend folder).
      - **JSON Schema:** Paste your schema JSON. You can use the default example provided in the text area.
      - Click **Validate and Create Schema**.
      - Watch the "Creation Log" for success or validation errors.
      - Save the successful connection to your profile.

3.  **Interact with Data (Module 2 & 4):**

      - Navigate to the **Query Executor** to insert raw data into your newly created tables.
      - Navigate to **Chat with DB**, select your saved connection, and ask plain English questions about your data.

4.  **Optimize Performance (Module 3):**

      - Navigate to **Optimize DB** to allow the AI DBA to profile your query logs and suggest missing indexes
-----

### Example JSON Schema

```json
{
  "tables": [
    {
      "name": "users",
      "description": "Users table",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "primary_key": true,
          "autoincrement": true,
          "nullable": false,
          "description": "users autogenerated db id"
        },
        {
          "name": "username",
          "type": "VARCHAR",
          "size": 50,
          "unique": true,
          "nullable": false,
          "description": "users username"
        },
        {
          "name": "email",
          "type": "VARCHAR",
          "size": 100,
          "unique": true,
          "nullable": true,
          "description": "users email"
        },
        {
          "name": "created_at",
          "type": "DATETIME",
          "nullable": false,
          "default": "CURRENT_TIMESTAMP",
          "description": "time at which record was created"
        },
        {
          "name": "is_active",
          "type": "BOOLEAN",
          "nullable": false,
          "default": "true",
          "description": "is user active?"
        }
      ]
    },
    {
      "name": "posts",,
      "description": "posts table"
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "primary_key": true,
          "autoincrement": true,
          "nullable": false,
          "description": "posts autogenerated db id"
        },
        {
          "name": "title",
          "type": "VARCHAR",
          "size": 200,
          "nullable": false,
          "description": "posts title"
        },
        {
          "name": "content",
          "type": "VARCHAR",
          "size": 10000,
          "description": "posts content"
        },
        {
          "name": "author_id",
          "type": "INTEGER",
          "nullable": true,
          "description": "user id who has posted this post"
        }
      ]
    }
  ],
  "relationships": [
    {
      "from_table": "posts",
      "from_column": "author_id",
      "to_table": "users",
      "to_column": "id",
      "on_delete": "SET NULL"
    }
  ],
  "indexes": [
    {
      "name": "idx_post_title",
      "table": "posts",
      "columns": ["title"]
    }
  ]
}
```
