from fastapi import APIRouter, Depends, HTTPException, Query
from services.search_service.infrastructure.repositories.message_search_repo import ClassicSearchRepository
from sqlalchemy.ext.asyncio import AsyncSession
from services.search_service.domain.search_request import SearchQuery
from services.search_service.api.schemas import SearchResponseSchema
from services.search_service.application.classic_search import ClassicSearchService
from libs.postgres.session import get_session

router = APIRouter(prefix="/search", tags=["Search"])
async def get_db_session_dependency() -> AsyncSession:
    async for session in get_session():
        yield session

@router.get(
    "/messages",
    response_model=SearchResponseSchema, 
    summary="Поиск сообщений",
    description="Ищет сообщения по заданной строке"
)

async def get_search_repository(
    session: AsyncSession = Depends(get_db_session_dependency)
) -> ClassicSearchRepository:
    return ClassicSearchRepository(session)

async def get_search_service(
    repo: ClassicSearchRepository = Depends(get_search_repository)
) -> ClassicSearchService:
    return ClassicSearchService(repo)

async def search_messages_route(
    query_string: str = Query(..., description="Строка для поиска сообщений"),
    session: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Обработчик для эндпоинта поиска сообщений.
    """
    try:
        search_query = SearchQuery(query_string)
        search_service = ClassicSearchService(session)
        search_response: SearchResponseSchema = await search_service.search(search_query)
        return search_response
        
    except ValueError as ve: 
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e: 
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при выполнении поиска.")