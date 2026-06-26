import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from sqlalchemy.dialects import postgresql

from services.search_service.domain.search_request import SearchQuery
from services.search_service.infrastructure.repositories.message_search_repo import ClassicSearchRepository


def compile_postgres(statement) -> str:
    return str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


class TestClassicSearchRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock()
        self.repo = ClassicSearchRepository(self.session)

    async def test_find_messages_uses_real_message_columns_simple_config_and_hidden_filter(self):
        message_id = uuid4()
        created_at = datetime.now()
        cursor = Mock()
        cursor.all.return_value = [
            SimpleNamespace(
                id=message_id,
                snippet="Highlighted snippet",
                created_at=created_at,
                rank=0.7,
            )
        ]
        self.session.execute.return_value = cursor

        results = await self.repo.find_messages(SearchQuery("hello"))

        statement = self.session.execute.await_args.args[0]
        sql = compile_postgres(statement).lower()
        self.assertIn("plainto_tsquery('simple', 'hello')", sql)
        self.assertIn("ts_headline('simple', messages.text", sql)
        self.assertIn("ts_rank(messages.tsv", sql)
        self.assertIn("messages.tsv @@ plainto_tsquery('simple', 'hello')", sql)
        self.assertIn("messages.hidden is false", sql)
        self.assertNotIn("messages.title", sql)
        self.assertNotIn("messages.content", sql)
        self.assertEqual(results[0].message_id, message_id)
        self.assertEqual(results[0].content_snippet, "Highlighted snippet")
        self.assertEqual(results[0].created_at, created_at)
        self.assertEqual(results[0].rank, 0.7)

    async def test_count_total_results_uses_same_fts_and_hidden_filter(self):
        cursor = Mock()
        cursor.scalar.return_value = 3
        self.session.execute.return_value = cursor

        total = await self.repo.count_total_results(SearchQuery("hello"))

        statement = self.session.execute.await_args.args[0]
        sql = compile_postgres(statement).lower()
        self.assertIn("count(*)", sql)
        self.assertIn("messages.tsv @@ plainto_tsquery('simple', 'hello')", sql)
        self.assertIn("messages.hidden is false", sql)
        self.assertEqual(total, 3)


if __name__ == "__main__":
    unittest.main()
