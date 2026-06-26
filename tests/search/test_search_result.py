import unittest
import uuid
from datetime import datetime
from services.search_service.domain.search_result import SearchResult

class TestSearchResult(unittest.TestCase):
    def test_should_create_valid_search_result(self):
        """Проверка успешного создания объекта с корректными данными"""
        # given
        message_id = uuid.uuid4()
        title = "Test Title"
        snippet = "Test snippet content"
        created_at = datetime.now()
        rank = 0.95

        # when
        result = SearchResult(
            message_id=message_id, 
            title=title, 
            content_snippet=snippet, 
            created_at=created_at, 
            rank=rank
        )

        # then
        self.assertEqual(result.message_id, message_id)
        self.assertEqual(result.title, title)
        self.assertEqual(result.content_snippet, snippet)
        self.assertEqual(result.created_at, created_at)
        self.assertEqual(result.rank, rank)

    def test_should_raise_error_when_message_id_is_missing(self):
        """Проверка, что исключение вызывается, если message_id не передан"""
        # given
        invalid_id = None
        
        # when / then
        with self.assertRaises(ValueError) as cm:
            SearchResult(
                message_id=invalid_id, 
                title="Title", 
                content_snippet="Snippet", 
                created_at=datetime.now(), 
                rank=0.5
            )
        
        self.assertEqual(str(cm.exception), "Message_id не може быть пустым")