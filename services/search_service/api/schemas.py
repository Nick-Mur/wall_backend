from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MessageResult(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор сообщения")
    snippet: str = Field(..., description="Фрагмент сообщения с подсветкой")
    created_at: datetime = Field(..., description="Дата создания сообщения")
    rank: float = Field(..., description="Релевантность сообщения")

    model_config = {
        "from_attributes": True,
    }


class SearchResponseSchema(BaseModel):
    results: list[MessageResult] = Field(default_factory=list, description="Список найденных сообщений")
    total_count: int = Field(0, description="Общее количество найденных сообщений")
