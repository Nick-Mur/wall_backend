from uuid import UUID

from pydantic import BaseModel, Field


class SubmitRequest(BaseModel):
    text: str = Field(..., max_length=5000)
    references: list[UUID] = Field(default_factory=list)
    author_id: UUID | None = None
