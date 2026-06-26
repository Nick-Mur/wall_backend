from uuid import UUID

# заглушка
class NullIndexer:
    async def index(self, message_id: UUID, text: str) -> None:
        pass
