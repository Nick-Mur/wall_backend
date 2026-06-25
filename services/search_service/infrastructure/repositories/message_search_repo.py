from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.sql import literal_column
from services.message_service.infrastructure.db_models.message import MessageModel
from services.search_service.domain.search_result import SearchResult
from services.search_service.domain.search_request import SearchQuery

class ClassicSearchRepository:
    """
    Read-only репозиторий для выполнения классического поиска.
    Работает с ORM-моделями SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_messages(self, query: SearchQuery) -> list[SearchResult]:
        """
        Выполняет поиск сообщений, используя ORM, и возвращает список внутренних моделей SearchResult.
        """
        tsquery_func_name = query.tsquery_func()
        tsquery_param = query.to_tsquery_string()
        tsquery_for_where = text(f"{tsquery_func_name}('russian', :tsquery_param)")
        tsquery_for_headline = text(f"{tsquery_func_name}('russian', :tsquery_param)")
        tsquery_for_rank = text(f"{tsquery_func_name}('russian', :tsquery_param)")
        
        stmt = (
            select(
                MessageModel.id,
                MessageModel.title,
                literal_column(f"ts_headline('russian', {MessageModel.content.name}, {tsquery_for_headline})").label("content_snippet"),
                MessageModel.created_at,
                literal_column(f"ts_rank({MessageModel.tsv.name}, {tsquery_for_rank})").label("rank")
            )
            .select_from(MessageModel)
            .where(
                literal_column(f"{MessageModel.tsv.name} @@ {tsquery_for_where}")
            )
            .order_by(literal_column("rank").desc())
        )
        
        params = {
            "tsquery_param": tsquery_param
        }
        
        cursor_results = await self.session.execute(stmt, params)
        rows = cursor_results.all()

        if not rows:
            return []
            
        results = []
        for row in rows:
            try:
                results.append(
                    SearchResult(
                        message_id=row.id,
                        title=row.title,
                        content_snippet=row.content_snippet,
                        created_at=row.created_at,
                        rank=row.rank
                    )
                )
            except ValueError as e:
                raise ValueError(f"Ошибка при создании SearchResult из строки БД: {e}. Строка: {row}")
        
        return results

    async def count_total_results(self, query: SearchQuery) -> int:
        """
        Подсчитывает общее количество сообщений, соответствующих запросу, используя ORM.
        """
        tsquery_func_name = query.tsquery_func()
        tsquery_param = query.to_tsquery_string()
        
        tsquery_for_where = text(f"{tsquery_func_name}('russian', :tsquery_param)")
        
        stmt = (
            select(func.count())
            .select_from(MessageModel)
            .where(
                literal_column(f"{MessageModel.tsv.name} @@ {tsquery_for_where}")
            )
        )
        
        params = {
            "tsquery_param": tsquery_param
        }
        
        result = await self.session.execute(stmt, params)
        
        return result.scalar() if result else 0