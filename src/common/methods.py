from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.common.constants import Constants

def custom_response(message, status_code=None, extra_keys=None):
    content = {"message": message}

    if extra_keys:
        content.update(extra_keys)

    if status_code:
        return JSONResponse(content=content, status_code=status_code)
    else:
        return JSONResponse(content=content)
    
def internal_server_error(detail=Constants.INTERNAL_SERVER_ERROR, status_code = status.HTTP_500_INTERNAL_SERVER_ERROR):
    raise HTTPException(
        detail = detail,
        status_code = status_code
    )