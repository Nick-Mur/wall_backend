from collections.abc import Callable

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .exception_handlers import handle_server_error, handle_validation_error


def create_app(
        title: str,
        routers: list | None = None,
        exception_handlers: dict[type[Exception], Callable] | None = None,
) -> FastAPI:
    app = FastAPI(title=title)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_server_error)
    if exception_handlers:
        for exc_class, handler in exception_handlers.items():
            app.add_exception_handler(exc_class, handler)
    if routers:
        for router in routers:
            app.include_router(router)

    return app
