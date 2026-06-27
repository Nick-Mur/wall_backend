from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SubmitRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    references: list[UUID] = Field(default_factory=list)
    author_id: UUID | None = None

    @field_validator("text", mode="before")
    @classmethod
    def strip_and_validate_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        value = value.strip()
        if not value:
            raise ValueError("Text must not be empty")
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Привет, this is a searchable message",
                "references": [],
                "author_id": None,
            }
        }
    }
