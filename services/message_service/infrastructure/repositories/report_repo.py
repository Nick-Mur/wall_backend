# TODO: Реализовать репозиторий жалоб.
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from services.message_service.infrastructure.db_models.report import ReportModel

class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message_id: UUID, reason: str) -> ReportModel:
        """Создать новую жалобу на сообщение."""
        report = ReportModel(
            message_id=message_id,
            reason=reason,
            status="pending"
        )
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_by_id(self, report_id: UUID) -> Optional[ReportModel]:
        """Найти жалобу по её идентификатору."""
        result = await self.session.execute(
            select(ReportModel).where(ReportModel.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_by_message_id(self, message_id: UUID) -> List[ReportModel]:
        """Получить список всех жалоб на конкретное сообщение."""
        result = await self.session.execute(
            select(ReportModel).where(ReportModel.message_id == message_id)
        )
        return list(result.scalars().all())

    async def update_status(self, report_id: UUID, new_status: str):
        """Обновить статус жалобы (например, 'reviewed' или 'dismissed')."""
        await self.session.execute(
            update(ReportModel)
            .where(ReportModel.id == report_id)
            .values(status=new_status)
        )
        await self.session.commit()
