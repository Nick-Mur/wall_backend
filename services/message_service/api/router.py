# TODO: Реализовать маршруты /messages/draft, /publish, /hide, /detach, /erase.
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from services.message_service.api.schemas import SubmitRequest
from services.message_service.application.publish import PublishMessage
from services.message_service.application.visibility import VisibilityUseCase

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/publish", status_code=201)
async def publish(
        req: SubmitRequest,
        use_case: PublishMessage = Depends()
):
    result = await use_case.process(req.text, req.references, req.author_id)
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["reason"])
    if result["status"] == "rejected":
        raise HTTPException(status_code=422, detail=result["reason"])
    return result


@router.post("/{message_id}/hide")
async def hide_message(message_id: UUID, use_case: VisibilityUseCase = Depends()):
    await use_case.hide(message_id)
    return {"status": "hidden"}


@router.post("/{message_id}/erase")
async def erase_message(message_id: UUID, use_case: VisibilityUseCase = Depends()):
    await use_case.erase(message_id)
    return {"status": "erased"}
