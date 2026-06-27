from sqlalchemy.ext.asyncio import AsyncSession

from services.search_service.domain.search_request import SearchQuery
from services.search_service.infrastructure.db_models.search_log import SearchLogModel


class SearchLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_log(self, query: SearchQuery, results_count: int):
        log_entry = SearchLogModel(
            query_string=query.query_string,
            results_count=results_count,
        )
        self.session.add(log_entry)
        await self.session.commit()
