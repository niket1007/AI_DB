from fastapi import FastAPI
from routers.routers import router
from Exceptions.custom_exception import custom_exception_handler, CustomException


api_description = """
Schema Parser and Creator API helps you to create table/indexes/realtionship from defined json format.

## Endpoints

* **GET /ping**
* **POST /create-schema**

## /ping
* Checks if server is responsive.

## /create-schema
* Parse and Validate the json structure
* Create db entites
"""

app = FastAPI(title="Schema Parser and Creator API",
              description=api_description,
              version="1.0.0")

app.include_router(router=router, tags=["Validator, Parser and Creator"])
app.add_exception_handler(CustomException, custom_exception_handler)

@app.get("/ping",tags=["API"])
def ping():
    return "Pinged"