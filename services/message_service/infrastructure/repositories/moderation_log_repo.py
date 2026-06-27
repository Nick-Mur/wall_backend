# TODO: Реализовать репозиторий логов модерации.
from services.message_service.infrastructure.db_models.moderation_log import ModerationLogModel
from services.message_service.moderation_module.moderation_result import ModerationResult
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession


class ModerationLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message_id: UUID, result: ModerationResult):
        details = {
            "warnings": [w.message for w in result.warnings],
            "reason": result.reason.message if result.reason else None
        }

        log_entry = ModerationLogModel(
            id=uuid4(),
            message_id=message_id,
            verdict=result.verdict.value,
            details=details
        )
        self.session.add(log_entry)
        await self.session.commit()
