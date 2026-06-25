import unittest
from unittest.mock import patch
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

    def test_to_tsquery_string_returns_correct_format(self):
        """Проверка, что метод to_tsquery_string возвращает исходную строку."""
        # given
        query_string = "тест с ! знаками . препинания :"

        # when
        query = SearchQuery(query_string=query_string)
        tsquery_string = query.to_tsquery_string()

        # then
        self.assertEqual(tsquery_string, query_string)


    def test_tsquery_func_returns_correct_function_name(self):
        """Проверка, что метод tsquery_func возвращает правильное имя функции."""
        # given
        query_string = "тест" 

        # when
        query = SearchQuery(query_string=query_string)
        func_name = query.tsquery_func()

        # then
        self.assertEqual(func_name, "plainto_tsquery")

if __name__ == "__main__":
    unittest.main()