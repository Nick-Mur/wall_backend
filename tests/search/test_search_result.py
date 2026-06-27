import unittest
import uuid
from datetime import datetime

from services.search_service.domain.search_result import SearchResult


class TestSearchResult(unittest.TestCase):
    def test_should_create_valid_search_result(self):
        """Проверка успешного создания объекта с корректными данными"""
        # given
        message_id = uuid.uuid4()
        snippet = "Test snippet content"
        created_at = datetime.now()
        rank = 0.95

        # when
        result = SearchResult(
            message_id=message_id,
            content_snippet=snippet,
            created_at=created_at,
            rank=rank,
        )

        # then
        self.assertEqual(result.message_id, message_id)
        self.assertEqual(result.content_snippet, snippet)
        self.assertEqual(result.created_at, created_at)
        self.assertEqual(result.rank, rank)
