MAX_SEARCH_QUERY_LENGTH = 250 #надо потом перенести в отдельный файл с константами

class SearchQuery:
    """
    Представляет собой поисковый запрос пользователя.
    """
    def __init__(self, query_string: str):
        self.query_string = query_string
        self._validate()

    def _validate(self) -> None:
        if not self.query_string:
            raise ValueError("Поисковой запрос не может быть пустым")
        
        if len(self.query_string) > MAX_SEARCH_QUERY_LENGTH:
            raise ValueError(
                f"Поисковой запрос слишком длинный")

    def to_tsquery_string(self) -> str:
        """
        Преобразует строку запроса в формат, понятный tsquery PostgreSQL.
        """
        if not self.query_string:
            return ""

        return self.query_string

    def tsquery_func(self) -> str:
        """Возвращает функцию tsquery (в нашем случае для подстрокового поиска только plainto_tsquery)"""

        return "plainto_tsquery"