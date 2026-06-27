from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from libs.postgres.session import get_session
from services.search_service.api.schemas import SearchResponseSchema
from services.search_service.application.classic_search import ClassicSearchService
from services.search_service.domain.search_request import SearchQuery
from services.search_service.infrastructure.repositories.message_search_repo import (
    ClassicSearchRepository,
)
from services.search_service.infrastructure.repositories.search_log_repo import (
    SearchLogRepository,
)

router = APIRouter(prefix="/search", tags=["Search"])


async def get_search_repository(session: AsyncSession = Depends(get_session)) -> ClassicSearchRepository:
    return ClassicSearchRepository(session)


async def get_search_log_repository(session: AsyncSession = Depends(get_session)) -> SearchLogRepository:
    return SearchLogRepository(session)


async def get_search_service(
    repo: ClassicSearchRepository = Depends(get_search_repository),
    log_repo: SearchLogRepository = Depends(get_search_log_repository),
) -> ClassicSearchService:
    return ClassicSearchService(repo, log_repo)


@router.get(
    "/messages",
    response_model=SearchResponseSchema,
    summary="Поиск сообщений",
    description="Ищет сообщения по заданной строке",
)
async def search_messages_route(
    query_string: str = Query(..., description="Строка для поиска сообщений"),
    search_service: ClassicSearchService = Depends(get_search_service),
):
    try:
        search_query = SearchQuery(query_string)
        return await search_service.search(search_query)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
