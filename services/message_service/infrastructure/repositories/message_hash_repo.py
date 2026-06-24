# TODO: Реализовать репозиторий хешей записей.
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from services.message_service.infrastructure.db_models.message_hash import MessageHashModel

class MessageHashRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, text_hash: str) -> bool:
        result = await self.session.execute(
            select(MessageHashModel).where(MessageHashModel.hash == text_hash)
        )
        return result.scalar_one_or_none() is not None

    async def save(self, text_hash: str, message_id: UUID):
        model = MessageHashModel(hash=text_hash, message_id=message_id)
        self.session.add(model)
        await self.session.commit()
