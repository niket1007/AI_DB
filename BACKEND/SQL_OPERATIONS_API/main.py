from fastapi import FastAPI
from routers.routers import router
from Exceptions.custom_exception import custom_exception_handler, CustomException


api_description = """
SQL Operations API

## Endpoints

* **GET /ping**
* **POST /text-to-sql**
* **POST /execute-sql**

## /ping
* Checks if server is responsive.

## /execute-sql
* Caller provide sql query and connection url
* Query is executed on database
* Response contain each query result (Result can be error or success)

## /text-to-sql
* Identify the query complexity
* Pass query complexity, json schema and question to SLM.
* Run output query on db and check if query is buggy
* If query is buggy then pass error to SLM
* Response contain final query
"""

app = FastAPI(title="SQL Operations API",
              description=api_description,
              version="1.0.0")

app.include_router(router=router)
app.add_exception_handler(CustomException, custom_exception_handler)

@app.get("/ping",tags=["API"])
def ping():
    return "Pinged"