from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from libs.postgres.session import get_session
from services.message_service.api.schemas import SubmitRequest
from services.message_service.application.publish import PublishMessage
from services.message_service.application.visibility import VisibilityError, VisibilityUseCase
from services.message_service.infrastructure.message_index import NullIndexer
from services.message_service.infrastructure.repositories.message_hash_repo import MessageHashRepository
from services.message_service.infrastructure.repositories.message_repo import MessageRepository
from services.message_service.moderation_module.pipeline import HardModerationPipeline, SoftModerationPipeline
from services.message_service.moderation_module.steps.ban_words import BanWordsStep
from services.message_service.moderation_module.steps.pii import PIIStep

router = APIRouter(prefix="/messages", tags=["Messages"])


async def get_db_session_dependency() -> AsyncSession:
    async for session in get_session():
        yield session


def build_hard_pipeline() -> HardModerationPipeline:
    return HardModerationPipeline([BanWordsStep(forbidden_words=[])])


def build_soft_pipeline() -> SoftModerationPipeline:
    return SoftModerationPipeline([PIIStep()])


async def get_publish_use_case(
    session: AsyncSession = Depends(get_db_session_dependency),
) -> PublishMessage:
    return PublishMessage(
        message_repo=MessageRepository(session),
        hash_repo=MessageHashRepository(session),
        hard_pipe=build_hard_pipeline(),
        soft_pipe=build_soft_pipeline(),
        indexer=NullIndexer(),
    )


async def get_visibility_use_case(
    session: AsyncSession = Depends(get_db_session_dependency),
) -> VisibilityUseCase:
    return VisibilityUseCase(MessageRepository(session))


@router.post("/publish", status_code=201)
async def publish(
    req: SubmitRequest,
    use_case: PublishMessage = Depends(get_publish_use_case),
):
    result = await use_case.process(req.text, req.references, req.author_id)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["reason"])
    if result["status"] == "rejected":
        raise HTTPException(status_code=422, detail=result["reason"])
    return result


@router.post("/{message_id}/hide")
async def hide_message(
    message_id: UUID,
    use_case: VisibilityUseCase = Depends(get_visibility_use_case),
):
    try:
        await use_case.hide(message_id)
    except VisibilityError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "hidden"}


@router.post("/{message_id}/detach")
async def detach_message(
    message_id: UUID,
    use_case: VisibilityUseCase = Depends(get_visibility_use_case),
):
    try:
        await use_case.detach(message_id)
    except VisibilityError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "detached"}


@router.post("/{message_id}/erase")
async def erase_message(
    message_id: UUID,
    use_case: VisibilityUseCase = Depends(get_visibility_use_case),
):
    try:
        await use_case.erase(message_id)
    except VisibilityError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "erased"}
