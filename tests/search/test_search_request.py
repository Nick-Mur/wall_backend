import unittest
from services.search_service.domain.search_request import SearchQuery, MAX_SEARCH_QUERY_LENGTH


class TestSearchQuery(unittest.TestCase):

    def test_init_with_valid_query_string(self):
        """Проверка успешного создания объекта с корректной строкой запроса."""
        # given
        query_string = "тест"

        # when
        query = SearchQuery(query_string=query_string)

        # then
        self.assertEqual(query.query_string, query_string)

    def test_should_raise_error_on_empty_query_string(self):
        """Проверка, что исключение ValueError выбрасывается при пустой строке запроса."""
        # given
        empty_string = ""

        # when / then
        with self.assertRaises(ValueError) as cm:
            SearchQuery(query_string=empty_string)

        self.assertEqual(str(cm.exception), "Поисковой запрос не может быть пустым")

    def test_should_raise_error_on_query_string_too_long(self):
        """Проверка, что исключение ValueError выбрасывается, если строка запроса слишком длинная."""
        # given
        too_long_string = "a" * (MAX_SEARCH_QUERY_LENGTH + 1)

        # when / then
        with self.assertRaises(ValueError) as cm:
            SearchQuery(query_string=too_long_string)

        self.assertEqual(str(cm.exception), "Поисковой запрос слишком длинный")

if __name__ == "__main__":
    unittest.main()
