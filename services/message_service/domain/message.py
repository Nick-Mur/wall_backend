# TODO: Описать доменную сущность записи и правила видимости/авторства.
from uuid import UUID
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from services.message_service.domain.exceptions.references_validation_error import ReferencesValidationError
from services.message_service.domain.exceptions.text_validation_error import TextValidationError

MAX_TEXT_LENGTH = 5000
MAX_REFERENCES_COUNT = 20


@dataclass
class Message:
    id: UUID
    text: str
    author_id: UUID | None = None
    hidden: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    references: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.text = self.text.strip()
        self._validate_text()
        self.references = self._deduplicate_references(self.references)
        self._validate_references()

    def _deduplicate_references(self, references: list[UUID] | None) -> list[UUID]:
        if references is None:
            return []
        return list(dict.fromkeys(references))

    def _validate_text(self) -> None:
        if not self.text:
            raise TextValidationError("Text must not be empty")
        if len(self.text) > MAX_TEXT_LENGTH:
            raise TextValidationError(f"Text too long. Max {MAX_TEXT_LENGTH} chars")

    def _validate_references(self) -> None:
        if len(self.references) > MAX_REFERENCES_COUNT:
            raise ReferencesValidationError(f"Message references must contain at most {MAX_REFERENCES_COUNT} items")
        for ref in self.references:
            if not isinstance(ref, UUID):
                raise ReferencesValidationError("Each references must be UUID")

    @property
    def is_visible(self) -> bool:
        return not self.hidden

    def hide(self) -> None:
        self.hidden = True

    def detach(self) -> None:
        self.author_id = None

    def erase(self) -> None:
        self.hide()
        self.detach()

    @classmethod
    def create(cls,
               text: str,
               references: list[UUID] | None = None,
               author_id: UUID | None = None
               ) -> "Message":
        return cls(
            id=uuid.uuid4(),
            text=text,
            author_id=author_id,
            hidden=False,
            created_at=datetime.now(),
            references=references or []
        )
