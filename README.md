# AI-DB: An Intelligent, Self-Optimising SQL Database with a Natural Language Interface

**AI-DB** is a dual-module application designed to simplify database schema creation and interaction. It features a **Schema Creator** that converts JSON definitions into actual SQL tables with strict validation, and a planned **Natural Language Interface** (Module 2) to chat with your data.

## 📋 Table of Contents

  - [Features](https://www.google.com/search?q=%23-features)
  - [Project Structure](https://www.google.com/search?q=%23-project-structure)
  - [Implementation Details](https://www.google.com/search?q=%23-implementation-details)
  - [Prerequisites](https://www.google.com/search?q=%23-prerequisites)
  - [Installation & Setup](https://www.google.com/search?q=%23-installation--setup)
  - [Execution Steps](https://www.google.com/search?q=%23-execution-steps)
  - [Usage Guide](https://www.google.com/search?q=%23-usage-guide)

-----

## 🚀 Features

### 1\. Schema Parser & Creator (Module 1)

  - **JSON-to-SQL Engine:** Define your database schema (tables, columns, relationships, indexes) using a simple JSON format.
  - **Strict Validation:** The backend validates the JSON structure before creation, checking for:
      - Duplicate table/column/index names.
      - Valid data types (INTEGER, VARCHAR, BOOLEAN, etc.).
      - Primary Key and Foreign Key integrity.
      - Logic rules (e.g., `autoincrement` only on Integers, `SET NULL` requires nullable columns).
  - **Universal Connectivity:** Uses **SQLAlchemy** under the hood, supporting SQLite, PostgreSQL, MySQL, and MSSQL.
  - **Visual Feedback:** Real-time logs in the UI showing the validation and creation process.

### 2\. Chat with DB (Module 2 - *Work in Progress*)

  - **Natural Language Interface:** A UI placeholder for a Text-to-SQL engine allowing users to query their database using plain English.
  - **Connection Management:** Saves connection strings from Module 1 for quick access.

### 3\. User Interface

  - **Streamlit Frontend:** A clean, responsive web interface.
  - **Authentication:** Built-in Login and Registration system (Session-based).

-----

## 📂 Project Structure

```text
AI_DB/
├── .gitignore
├── README.md
├── requirements.txt           # Python dependencies
├── BACKEND/
│   └── SCHEMA_PARSER_CREATOR_API/
│       ├── main.py            # Entry point for FastAPI backend
│       ├── Exceptions/        # Custom exception handling
│       ├── models/            # Pydantic models for JSON validation
│       ├── routers/           # API endpoints
│       └── services/          # Core logic (Validation & SQLAlchemy generation)
└── UI/
    ├── .env                   # Environment variables (API URL)
    ├── main.py                # Entry point for Streamlit Frontend
    ├── static/                # Helper data (JSON examples, connection guides)
    └── ui_pages/              # Individual UI pages (Login, Creator, Chat)
```

-----

## 🛠 Implementation Details

### Backend (FastAPI)

The backend is built using **FastAPI** and follows a layered architecture:

1.  **Router (`routers/routers.py`):** Exposes the `/create-schema` endpoint. Accepts a JSON payload containing the DB connection string and the Schema JSON.
2.  **Validator (`services/schema_validator.py`):**
      - Converts raw JSON into Pydantic models (`models/json_model.py`).
      - Runs complex logical checks (e.g., ensuring a Foreign Key points to a valid Primary Key).
      - Returns detailed error messages if the schema is invalid.
3.  **Parser & Creator (`services/schema_parser.py`):**
      - Dynamically constructs **SQLAlchemy** `Table`, `Column`, and `Index` objects based on the validated models.
      - Uses `Asyncio` to handle the request asynchronously.
      - Executes the DDL (Data Definition Language) statements against the target database using a transaction.

### Frontend (Streamlit)

The frontend utilizes **Streamlit** for rapid UI development:

1.  **State Management:** Uses `st.session_state` to handle user login sessions, page navigation (`login` -\> `creator` -\> `chat`), and storing active database connections.
2.  **API Integration:** Uses the `requests` library to send the JSON schema to the FastAPI backend and stream the response logs back to the user.

-----

## 📋 Prerequisites

  * **Python 3.10+** (Project developed on 3.12)
  * **Pip** (Python Package Manager)

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

```bash
# From the root AI_DB folder
cd BACKEND/SCHEMA_PARSER_CREATOR_API

# Run the server
fastapi dev .\main.py
```

*You should see: 
- `Backend Server running on http://127.0.0.1:8000`*
- `OpenAPI doc server running on http://127.0.0.1:8000/docs`*

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
      - Click **Register** to create a dummy account (e.g., Username: `user`, Password: `pass`).
      - **Login** with those credentials.

2.  **Create a Database Schema:**

      - Navigate to **Schema Creator** from the sidebar.
      - **Connection String:** Enter a valid SQLAlchemy connection string.
          - *For testing, use SQLite:* `sqlite:///test_db.db` (This creates a file named `test_db.db` in the backend folder).
      - **JSON Schema:** Paste your schema JSON. You can use the default example provided in the text area.
      - Click **Validate and Create Schema**.
      - Watch the "Creation Log" for success or validation errors.

3.  **Save Connection:**

      - Upon success, a "Save Connection" form appears. Give it a name (e.g., "My Test DB") and save it.

4.  **Chat (Mockup):**

      - Navigate to **Chat with DB**.
      - Select your saved connection.
      - *Note: The actual Text-to-SQL functionality is currently a placeholder.*

-----

### Example JSON Schema

```json
{
  "tables": [
    {
      "name": "users",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "primary_key": true,
          "autoincrement": true,
          "nullable": false
        },
        {
          "name": "username",
          "type": "VARCHAR",
          "size": 50,
          "unique": true,
          "nullable": false
        },
        {
          "name": "email",
          "type": "VARCHAR",
          "size": 100,
          "unique": true,
          "nullable": true
        },
        {
          "name": "created_at",
          "type": "DATETIME",
          "nullable": false,
          "default": "CURRENT_TIMESTAMP"
        },
        {
          "name": "is_active",
          "type": "BOOLEAN",
          "nullable": false,
          "default": "true"
        }
      ]
    },
    {
      "name": "posts",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "primary_key": true,
          "autoincrement": true,
          "nullable": false
        },
        {
          "name": "title",
          "type": "VARCHAR",
          "size": 200,
          "nullable": false
        },
        {
          "name": "content",
          "type": "VARCHAR",
          "size": 10000
        },
        {
          "name": "author_id",
          "type": "INTEGER",
          "nullable": true
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
