class SearchResponse:
    """
    Объект ответа поиска, содержащий список результатов поиска.
    """

    def __init__(self, results, total_count=0):
        self.results = results
        self.total_count = total_count

    def has_results(self) -> bool:
        """Возвращает True, если в ответе есть хотя бы один результат."""
        return len(self.results) > 0

    def create_empty(cls) -> "SearchResponse":
        """Создает пустой ответ если результатов не найдено"""
        return cls(results=[], total_count=0)