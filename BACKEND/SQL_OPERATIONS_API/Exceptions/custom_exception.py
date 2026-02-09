from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, message: dict, type: str|None = None,):
        self.type = type
        self.message = message

def custom_exception_handler(request: Request, exec: CustomException):
    if exec.type == "VALIDATION_FAILURE":
        return JSONResponse(status_code=400,
                            content=exec.message)
    else:
        return JSONResponse(status_code=500, content=str(exec))
