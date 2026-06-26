import unittest
from unittest.mock import AsyncMock
from services.search_service.application.classic_search import ClassicSearchService
from services.search_service.domain.search_request import SearchQuery
from services.search_service.domain.search_result import SearchResult
from uuid import uuid4
from datetime import datetime

class TestClassicSearchService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_search_repo = AsyncMock()
        self.mock_log_repo = AsyncMock()
        
        self.service = ClassicSearchService(
            repository=self.mock_search_repo, 
            log_repo=self.mock_log_repo
        )

    async def test_search_should_return_empty_on_empty_query(self):
        """Проверка: если запрос пустой, поиск не выполняется"""
        # given
        query = SearchQuery(query_string="")

        # when
        result = await self.service.search(query)

        # then
        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.results), 0)
        self.mock_search_repo.find_messages.assert_not_called()

    async def test_search_should_return_results_and_log(self):
        """Проверка: успешный поиск возвращает результаты и пишет лог"""
        # given
        query = SearchQuery(query_string="test")
        
        mock_result = SearchResult(
            message_id=uuid4(),
            title="Test Title",
            content_snippet="Test Snippet",
            created_at=datetime.now(),
            rank=0.9
        )
        
        self.mock_search_repo.find_messages.return_value = [mock_result]
        self.mock_search_repo.count_total_results.return_value = 1

        # when
        result = await self.service.search(query)

        # then
        self.assertEqual(result.total_count, 1)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].title, "Test Title")
        self.mock_log_repo.save_log.assert_called_once_with(query, 1)

    async def test_search_should_raise_error_when_logging_fails(self):
        """Проверка: если логирование падает, сервис выбрасывает исключение"""
        # given
        query = SearchQuery(query_string="test")
        self.mock_search_repo.find_messages.return_value = []
        self.mock_search_repo.count_total_results.return_value = 0
        self.mock_log_repo.save_log.side_effect = Exception("DB Error")

        # when / then
        with self.assertRaises(ValueError) as cm:
            await self.service.search(query)
        
        self.assertIn("Не удалось записать лог поиска", str(cm.exception))