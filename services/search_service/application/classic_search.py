from services.search_service.domain.search_request import SearchQuery
from services.search_service.domain.search_result import SearchResult
from services.search_service.domain.search_response import SearchResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class ClassicSearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _build_sql_query(self, query: SearchQuery):
        """
        Формирует SQL-запрос и возвращает его в виде строки и словаря параметров.
        """
        tsquery_func_name = query.tsquery_func()
        tsquery_param = query.to_tsquery_string()
        
        #пока как язык запроса указываем именно русский, потом можно расширить на другие языки
        sql = f"""
        SELECT
            m.message_id,
            m.title,
            ts_headline(
                'russian', m.content, {tsquery_func_name}('russian', :tsquery_param)
            ) AS content_snippet,
            m.created_at,
            ts_rank(m.tsv, {tsquery_func_name}('russian', :tsquery_param)) AS rank
        FROM
            messages AS m
        WHERE
            m.tsv @@ {tsquery_func_name}('russian', :tsquery_param)
        ORDER BY
            rank DESC
        """
        
        params = {
            "tsquery_param": tsquery_param
        }
        
        return sql, params

    async def _count_total_results(self, query: SearchQuery) -> int:
        """
        Выполняет отдельный запрос для подсчёта общего числа совпадений
        """
        tsquery_func_name = query.tsquery_func()
        tsquery_param = query.to_tsquery_string()
        
        count_sql_text = text(f"""
        SELECT COUNT(*)
        FROM messages
        WHERE tsv @@ {tsquery_func_name}('russian', :tsquery_param);
        """)
        
        result = await self.session.execute(count_sql_text, {"tsquery_param": tsquery_param})
        
        return result.scalar()


    async def search(self, query: SearchQuery) -> SearchResponse:
        """
        Выполняет асинхронный поиск сообщений на основе запроса
        """
        if not query.query_string:
            return SearchResponse.create_empty()
            
        sql_query_str, params = await self._build_sql_query(query)
        query_text = text(sql_query_str)
        cursor_results = await self.session.execute(query_text, params)
        rows = cursor_results.all()

        if not rows:
            return SearchResponse.create_empty()
            
        results = []
        for row in rows:
            try:
                results.append(
                    SearchResult(
                        message_id=row[0],
                        title=row[1],
                        content_snippet=row[2],
                        created_at=row[3],
                        rank=row[4]
                    )
                )
            except ValueError as e:
                print(f"Ошибка при создании SearchResult: {e}. Строка: {row}")
                continue 

        total_count = await self._count_total_results(query)
        
        return SearchResponse(
            results=results,
            total_count=total_count
        )