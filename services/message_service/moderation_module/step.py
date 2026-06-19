# TODO: Описать интерфейс шага модерации.
from abc import ABC, abstractmethod
from typing import Optional


# задает только шаблон для других классов
class ModerationStep(ABC):
    @abstractmethod
    async def process(self, text: str) -> Optional[str]:
        pass
