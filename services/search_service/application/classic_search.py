from services.search_service.api.schemas import SearchResponseSchema, MessageResult
from services.search_service.infrastructure.repositories.message_search_repo import ClassicSearchRepository
from services.search_service.domain.search_request import SearchQuery

class ClassicSearchService:
    def __init__(self, repository: ClassicSearchRepository):
        self.repository = repository

    async def search(self, query: SearchQuery) -> SearchResponseSchema:
        if not query.query_string:
            return SearchResponseSchema.create_empty()

        internal = await self.repository.find_messages(query)
        total   = await self.repository.count_total_results(query)

        api_results = [
            MessageResult(
                id=r.message_id,
                title=r.title,
                snippet=r.content_snippet,
                created_at=r.created_at,
                rank=r.rank,
            )
            for r in internal
        ]

        return SearchResponseSchema(results=api_results, total_count=total)