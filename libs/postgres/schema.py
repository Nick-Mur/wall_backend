from libs.postgres.base import Base
from libs.postgres.session import engine
from services.message_service.infrastructure.db_models.message import MessageModel
from services.message_service.infrastructure.db_models.message_hash import MessageHashModel
from services.message_service.infrastructure.db_models.message_link import MessageLinkModel
from services.message_service.infrastructure.db_models.moderation_log import ModerationLogModel
from services.message_service.infrastructure.db_models.report import ReportModel
from services.search_service.infrastructure.db_models.search_log import SearchLogModel

_MODELS = (
    MessageModel,
    MessageHashModel,
    MessageLinkModel,
    ModerationLogModel,
    ReportModel,
    SearchLogModel,
)


async def init_db_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
