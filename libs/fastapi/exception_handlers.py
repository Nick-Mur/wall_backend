# TODO: Реализовать общие обработчики ошибок HTTP/API.
from fastapi import Request, status
from fastapi.responses import JSONResponse


async def handle_validation_error(request: Request, exception: Exception):
    """400"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exception.__class__.__name__,
            "message": str(exception)
        }
    )
async def handle_server_error(request: Request, exception: Exception):
    """500"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred."
        }
    )

