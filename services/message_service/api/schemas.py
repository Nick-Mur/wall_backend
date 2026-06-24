# TODO: Описать Pydantic-схемы SubmitRequest, PublishRequest, MessageResponse.
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from datetime import datetime


class SubmitRequest(BaseModel):
    text: str = Field(..., max_length=5000)
    references: List[UUID] = Field(default_factory=list)
    author_id: Optional[UUID] = None


class PublishRequest(BaseModel):
    text: str
    references: List[UUID] = Field(default_factory=list)
    author_id: Optional[UUID] = None

class MessageResponse(BaseModel):
    id: UUID
    text: str
    author_id: Optional[UUID] = None
    created_at: datetime
    hidden: bool
    references: List[UUID]

    class Config:
        from_attributes = True