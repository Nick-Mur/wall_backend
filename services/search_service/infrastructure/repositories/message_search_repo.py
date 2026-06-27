from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.message_service.infrastructure.db_models.message import MessageModel
from services.search_service.domain.search_request import SearchQuery
from services.search_service.domain.search_result import SearchResult

# Keep FTS config inline in SQL: ts_headline('simple', ...).
_TS_CONFIG = literal_column("'simple'")


class ClassicSearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_messages(self, query: SearchQuery) -> list[SearchResult]:
        tsquery = self._tsquery(query)
        snippet = func.ts_headline(_TS_CONFIG, MessageModel.text, tsquery).label("snippet")
        rank = func.ts_rank(MessageModel.tsv, tsquery).label("rank")

        stmt = (
            select(
                MessageModel.id,
                snippet,
                MessageModel.created_at,
                rank,
            )
            .select_from(MessageModel)
            .where(
                MessageModel.tsv.op("@@")(tsquery),
                MessageModel.hidden.is_(False),
            )
            .order_by(rank.desc())
        )

        cursor_results = await self.session.execute(stmt)
        rows = cursor_results.all()

        return [
            SearchResult(
                message_id=row.id,
                content_snippet=row.snippet,
                created_at=row.created_at,
                rank=row.rank,
            )
            for row in rows
        ]

    async def count_total_results(self, query: SearchQuery) -> int:
        tsquery = self._tsquery(query)

        stmt = (
            select(func.count())
            .select_from(MessageModel)
            .where(
                MessageModel.tsv.op("@@")(tsquery),
                MessageModel.hidden.is_(False),
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar() if result else 0

    def _tsquery(self, query: SearchQuery):
        tsquery_func = getattr(func, query.tsquery_func())
        return tsquery_func(_TS_CONFIG, query.to_tsquery_string())
