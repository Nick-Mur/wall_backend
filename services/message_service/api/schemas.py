from uuid import UUID

from pydantic import BaseModel, Field


class SubmitRequest(BaseModel):
    text: str = Field(..., max_length=5000)
    references: list[UUID] = Field(default_factory=list)
    author_id: UUID | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Привет, this is a searchable message",
                "references": [],
                "author_id": None,
            }
        }
    }
