from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def handle_validation_error(request: Request, exception: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": exception.__class__.__name__,
            "detail": [_clean_validation_error(error) for error in exception.errors()],
        },
    )


def _clean_validation_error(error: dict) -> dict:
    error = dict(error)
    error.pop("ctx", None)
    return jsonable_encoder(error)


async def handle_server_error(request: Request, exception: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred.",
        },
    )

