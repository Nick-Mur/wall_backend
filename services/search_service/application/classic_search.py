from services.search_service.api.schemas import MessageResult, SearchResponseSchema
from services.search_service.domain.search_request import SearchQuery
from services.search_service.infrastructure.repositories.message_search_repo import ClassicSearchRepository
from services.search_service.infrastructure.repositories.search_log_repo import SearchLogRepository


class ClassicSearchService:
    def __init__(self, repository: ClassicSearchRepository, log_repo: SearchLogRepository):
        self.repository = repository
        self.log_repo = log_repo

    async def search(self, query: SearchQuery) -> SearchResponseSchema:
        internal = await self.repository.find_messages(query)
        total = await self.repository.count_total_results(query)

        try:
            await self.log_repo.save_log(query, total)
        except Exception as e:
            raise ValueError(f"Не удалось записать лог поиска: {e}")

        api_results = [
            MessageResult(
                id=r.message_id,
                snippet=r.content_snippet,
                created_at=r.created_at,
                rank=r.rank,
            )
            for r in internal
        ]

        return SearchResponseSchema(results=api_results, total_count=total)
