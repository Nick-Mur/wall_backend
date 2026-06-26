from uuid import UUID
from datetime import datetime

class SearchResult:
    """
    Один резульат поиска - одно найденное по запросу сообщение
    """
    def __init__(self, message_id: UUID, title: str, content_snippet: str, created_at: datetime, rank: float):
        self.message_id = message_id
        self.title = title
        self.content_snippet = content_snippet
        self.created_at = created_at
        self.rank = rank
        self._validate()

    def _validate(self) -> None:
        if not self.message_id:
            raise ValueError("Message_id не може быть пустым")