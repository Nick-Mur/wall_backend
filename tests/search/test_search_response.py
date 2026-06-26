import unittest
from datetime import datetime
import uuid
from services.search_service.domain.search_response import SearchResponse

class MockSearchResult:
    def __init__(self, message_id, title, content_snippet, created_at, rank):
        self.message_id = message_id
        self.title = title
        self.content_snippet = content_snippet
        self.created_at = created_at
        self.rank = rank

class TestSearchResponse(unittest.TestCase):

    def test_init_with_results_and_total_count(self):
        """Проверка инициализации с данными"""
        # given
        mock_result1 = MockSearchResult(uuid.uuid4(), "Title 1", "Snippet 1", datetime.now(), 0.9)
        mock_result2 = MockSearchResult(uuid.uuid4(), "Title 2", "Snippet 2", datetime.now(), 0.8)
        results = [mock_result1, mock_result2]
        total_count = 5

        # when
        response = SearchResponse(results=results, total_count=total_count)

        # then
        self.assertEqual(response.results, results)
        self.assertEqual(response.total_count, total_count)

    def test_init_with_results_and_default_total_count(self):
        """Проверка инициализации с результатами и значением total_count по умолчанию"""
        # given
        mock_result = MockSearchResult(uuid.uuid4(), "Title", "Snippet", datetime.now(), 0.7)
        results = [mock_result]

        # when
        response = SearchResponse(results=results)

        # then
        self.assertEqual(response.results, results)
        self.assertEqual(response.total_count, 0)

    def test_init_with_empty_results_and_default_total_count(self):
        """Проверка инициализации с пустым списком результатов и значением total_count по умолчанию"""
        # given
        results = []

        # when
        response = SearchResponse(results=results)

        # then
        self.assertEqual(response.results, results)
        self.assertEqual(response.total_count, 0)

    def test_has_results_when_results_not_empty(self):
        """Проверка has_results, когда есть результаты"""
        # given
        mock_result = MockSearchResult(uuid.uuid4(), "Title", "Snippet", datetime.now(), 0.6)
        results = [mock_result]
        response = SearchResponse(results=results)

        # when
        has_results = response.has_results()

        # then
        self.assertTrue(has_results)

    def test_has_results_when_results_is_empty(self):
        """Проверка has_results, когда результатов нет"""
        # given
        results = []
        response = SearchResponse(results=results)

        # when
        has_results = response.has_results()

        # then
        self.assertFalse(has_results)

    def test_create_empty_class_method(self):
        """Проверка работы статического метода create_empty"""

        # when
        empty_response = SearchResponse.create_empty()

        # then
        self.assertIsInstance(empty_response, SearchResponse)
        self.assertEqual(empty_response.results, [])
        self.assertEqual(empty_response.total_count, 0)
        self.assertFalse(empty_response.has_results())

    def test_create_empty_is_idempotent(self):
        """Проверка, что create_empty всегда возвращает один и тот же вид пустого ответа"""
        # given
        response1 = SearchResponse.create_empty()
        response2 = SearchResponse.create_empty()
        
        # when/then
        self.assertEqual(response1.results, response2.results)
        self.assertEqual(response1.total_count, response2.total_count)
        self.assertEqual(response1.has_results(), response2.has_results())

if __name__ == "__main__":
    unittest.main()