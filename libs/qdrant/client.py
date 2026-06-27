# TODO: Реализовать фабрику Qdrant-клиента.
from typing import Any

from qdrant_client import AsyncQdrantClient


class QdrantClientFactory:
    def __init__(self, config: dict[str, Any]):
        # ищем qdrant в конфиге
        self._cfg = config.get("qdrant", {})

        # параметры подключения
        self._host = self._cfg.get("host", "localhost")
        self._port = self._cfg.get("port")
        self._api_key = self._cfg.get("api_key")
        self._timeout = self._cfg.get("timeout", 10)  # максимальное время ожидания ответа от сервера

    def create_async_client(self) -> AsyncQdrantClient:
        return AsyncQdrantClient(
            host=self._host,
            port=self._port,
            api_key=self._api_key,
            timeout=self._timeout
        )
