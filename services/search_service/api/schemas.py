from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class MessageResult(BaseModel):
    """
    Pydantic-схема для представления одного сообщения в ответе API.
    """

    id: UUID = Field(..., description="Уникальный идентификатор сообщения")
    title: str = Field(..., description="Заголовок сообщения")
    snippet: str = Field(..., description="Фрагмент сообщения с подсветкой") 
    created_at: datetime = Field(..., description="Дата создания сообщения")
    rank: float = Field(..., description="Релевантность сообщения")
    
    model_config = {
        "from_attributes": True 
                               
    }

class SearchResponseSchema(BaseModel):
    """
    Pydantic-схема для всего ответа API на поисковый запрос.
    """

    results: list[MessageResult] = Field(default_factory=list, description="Список найденных сообщений")
    total_count: int = Field(0, description="Общее количество найденных сообщений")