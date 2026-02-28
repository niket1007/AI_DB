from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, message: dict, type: str|None = None,):
        self.type = type
        self.message = message

def custom_exception_handler(request: Request, exec: CustomException):
    status_code = 500
    if exec.type == "VALIDATION_FAILURE":
        status_code=400
    print("API Error Response", exec.message)
    return JSONResponse(status_code=status_code, content=exec.message)
