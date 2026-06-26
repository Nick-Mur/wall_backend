# TODO: Реализовать репозиторий записей.
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from services.message_service.infrastructure.db_models.message import MessageModel
from services.message_service.domain.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: Message):
        model = MessageModel(id=message.id, text=message.text, author_id=message.author_id, hidden=message.hidden,
                             created_at=message.created_at)
        self.session.add(model)
        await self.session.commit()

    async def get_by_id(self, message_id: UUID):
        res = await self.session.execute(select(MessageModel).where(MessageModel.id == message_id))
        model = res.scalar_one_or_none()
        if not model:
            return None
        return Message(id=model.id, text=model.text, author_id=model.author_id, hidden=model.hidden,
                       created_at=model.created_at)
    async def update(self, message: Message):
        await self.session.execute(
            update(MessageModel)
            .where(MessageModel.id == message.id)
            .values(hidden=message.hidden, author_id=message.author_id)
        )
        await self.session.commit()
