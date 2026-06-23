# TODO: Реализовать сценарий публикации черновика, hard moderation, проверку дублей и индексацию.
from typing import List, Optional
from uuid import UUID
import hashlib
from services.message_service.domain.message import Message


class PublishMessage:
    def __init__(self, message_repo, hash_repo, hard_pipe, soft_pipe, indexer):
        self.repo = message_repo
        self.hash_repo = hash_repo
        self.soft_pipe = soft_pipe
        self.hard_pipe = hard_pipe
        self.indexer = indexer

    async def process(self, text: str, references: List[UUID], author_id: Optional[UUID] = None):
        # проверка на дубликат по хэшу
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        if await self.hash_repo.exists(text_hash):
            return {"status": "error", "code": 409, "reason": "Duplicate detected"}

        # хард модерация
        hard_res = await self.hard_pipe.validate(text)
        if hard_res.is_rejected:
            return {"status": "rejected", "code": 422, "reason": hard_res.reason.message}

        message = Message.create(text=text, references=references, author_id=author_id)

        # мягкая модерация
        soft_res = await self.soft_pipe.validate(text)
        warnings = [w.message for w in soft_res.warnings]

        await self.repo.save(message)
        await self.hash_repo.save(text_hash, message.id)
        await self.indexer.index(message.id, message.text)

        return {
            "status": "published",
            "message_id": message.id,
            "warnings" : warnings,
            "code": 201
        }
