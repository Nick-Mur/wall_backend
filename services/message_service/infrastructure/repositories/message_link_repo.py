# TODO: Реализовать репозиторий связей между записями.
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from services.message_service.infrastructure.db_models.message_link import MessageLinkModel


class MessageLinkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_links(self, source_id: UUID, target_ids: List[UUID]):
        if not target_ids:
            return

        links = [
            MessageLinkModel(source_id=source_id, target_id=t_id)
            for t_id in target_ids
        ]
        self.session.add_all(links)
        await self.session.commit()