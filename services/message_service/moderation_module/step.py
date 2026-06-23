# TODO: Описать интерфейс шага модерации.
from abc import ABC, abstractmethod
from typing import Optional, Union

from services.message_service.domain.moderation import ModerationWarning, ModerationReason


# задает только шаблон для других классов
class ModerationStep(ABC):
    @abstractmethod
    async def process(self, text: str) -> Optional[Union[ModerationWarning, ModerationReason]]:
        pass
