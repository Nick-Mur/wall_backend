# TODO: Реализовать фабрику FastAPI-приложений.
from fastapi import FastAPI
from typing import List, Dict, Type, Callable, Optional

from fastapi.exceptions import RequestValidationError

from .exception_handlers import handle_server_error, handle_validation_error


def create_app(
        title: str,
        routers: Optional[List] = None,
        exception_handlers: Optional[Dict[Type[Exception], Callable]] = None
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
