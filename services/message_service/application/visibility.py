from uuid import UUID


class VisibilityError(ValueError):
    pass


class VisibilityUseCase:
    def __init__(self, message_repo):
        self.repo = message_repo

    async def hide(self, message_id: UUID):
        msg = await self._get_message(message_id)
        msg.hide()
        await self.repo.update(msg)

    async def detach(self, message_id: UUID):
        msg = await self._get_message(message_id)
        msg.detach()
        await self.repo.update(msg)

    async def erase(self, message_id: UUID):
        msg = await self._get_message(message_id)
        msg.erase()
        await self.repo.update(msg)

    async def _get_message(self, message_id: UUID):
        msg = await self.repo.get_by_id(message_id)
        if not msg:
            raise VisibilityError("Message not found")
        return msg

