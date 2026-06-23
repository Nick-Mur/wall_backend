# TODO: Реализовать общие зависимости FastAPI.
from typing import Optional
from fastapi import Header

async def get_request_id(x_request_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_request_id
