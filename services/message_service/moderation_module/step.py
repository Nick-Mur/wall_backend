from abc import ABC, abstractmethod

from services.message_service.domain.moderation import ModerationReason, ModerationWarning


class ModerationStep(ABC):
    @abstractmethod
    async def process(self, text: str) -> ModerationWarning | ModerationReason | None:
        ...
