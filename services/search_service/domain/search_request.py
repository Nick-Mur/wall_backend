MAX_SEARCH_QUERY_LENGTH = 250

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

