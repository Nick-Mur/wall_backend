# TODO: Реализовать сценарии hide, detach, erase.
from uuid import UUID

class VisibilityError(ValueError):
    pass

class VisibilityUseCase:
    def __init__(self, message_repo):
        self.repo = message_repo

    async def hide(self, message_id: UUID):
        msg = await self.repo.get_by_id(message_id)
        if not msg:
            raise VisibilityError("Message not found")
        msg.hide()
        await self.repo.update(msg)

    async def detach(self, message_id: UUID):
        msg = await self.repo.get_by_id(message_id)
        if not msg:
            raise VisibilityError("Message not found")
        msg.detach()
        await self.repo.update(msg)

    async def erase(self, message_id: UUID):
        msg = await self.repo.get_by_id(message_id)
        if not msg:
            raise VisibilityError("Message not found")
        msg.erase()
        await self.repo.update(msg)

