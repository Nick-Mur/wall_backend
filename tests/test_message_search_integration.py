from uuid import UUID, uuid4

import pytest
from sqlalchemy import select

from services.message_service.api.router import get_publish_use_case
from services.message_service.application.publish import PublishMessage
from services.message_service.infrastructure.message_index import NullIndexer
from services.message_service.infrastructure.repositories.message_hash_repo import (
    MessageHashRepository,
)
from services.message_service.infrastructure.repositories.message_repo import MessageRepository
from services.message_service.main import app as message_app
from services.message_service.moderation_module.pipeline import (
    HardModerationPipeline,
    SoftModerationPipeline,
)
from services.message_service.moderation_module.steps.ban_words import BanWordsStep
from services.message_service.moderation_module.steps.pii import PIIStep
from services.search_service.infrastructure.db_models.search_log import SearchLogModel
from services.message_service.infrastructure.db_models.message import MessageModel
from tests.conftest import TestSessionFactory


async def publish_message(message_client, text: str, author_id: str | None = None):
    payload = {"text": text, "references": []}
    if author_id:
        payload["author_id"] = author_id

    response = await message_client.post("/messages/publish", json=payload)
    assert response.status_code == 201
    return response.json()


async def search_messages(search_client, query: str):
    response = await search_client.get(
        "/search/messages",
        params={"query_string": query},
    )
    assert response.status_code == 200
    return response.json()


@pytest.mark.asyncio
async def test_publish_message_then_search_finds_it(message_client, search_client):
    published = await publish_message(message_client, "Integration searchable message")

    body = await search_messages(search_client, "searchable")

    assert body["total_count"] == 1
    assert body["results"][0]["id"] == published["message_id"]
    assert "searchable" in body["results"][0]["snippet"].lower()
    assert body["results"][0]["rank"] > 0


@pytest.mark.asyncio
async def test_search_finds_multilingual_messages(message_client, search_client):
    english = await publish_message(message_client, "English alpha marker")
    russian = await publish_message(message_client, "Русский бета маркер")
    german = await publish_message(message_client, "Deutsch gamma kennzeichen")

    english_result = await search_messages(search_client, "alpha")
    russian_result = await search_messages(search_client, "бета")
    german_result = await search_messages(search_client, "kennzeichen")

    assert english_result["results"][0]["id"] == english["message_id"]
    assert russian_result["results"][0]["id"] == russian["message_id"]
    assert german_result["results"][0]["id"] == german["message_id"]


@pytest.mark.asyncio
async def test_search_returns_ranked_results_total_count_and_snippet(message_client, search_client):
    high_rank = await publish_message(message_client, "ranktoken ranktoken ranktoken primary")
    low_rank = await publish_message(message_client, "ranktoken secondary")

    body = await search_messages(search_client, "ranktoken")

    assert body["total_count"] == 2
    assert [result["id"] for result in body["results"]] == [
        high_rank["message_id"],
        low_rank["message_id"],
    ]
    assert body["results"][0]["rank"] >= body["results"][1]["rank"]
    assert "ranktoken" in body["results"][0]["snippet"].lower()


@pytest.mark.asyncio
async def test_hard_rejected_message_is_not_searchable(message_client, search_client):
    async def reject_spam_publish_use_case():
        async with TestSessionFactory() as session:
            yield PublishMessage(
                message_repo=MessageRepository(session),
                hash_repo=MessageHashRepository(session),
                hard_pipe=HardModerationPipeline([BanWordsStep(forbidden_words=["blockedword"])]),
                soft_pipe=SoftModerationPipeline([PIIStep()]),
                indexer=NullIndexer(),
            )

    message_app.dependency_overrides[get_publish_use_case] = reject_spam_publish_use_case
    try:
        response = await message_client.post(
            "/messages/publish",
            json={"text": "This message has blockedword", "references": []},
        )
    finally:
        message_app.dependency_overrides.pop(get_publish_use_case, None)

    assert response.status_code == 422
    body = await search_messages(search_client, "blockedword")
    assert body["total_count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_soft_warning_message_is_published_and_searchable(message_client, search_client):
    response = await message_client.post(
        "/messages/publish",
        json={
            "text": "Contact me at soft-warning@example.com about searchable pii",
            "references": [],
        },
    )

    assert response.status_code == 201
    published = response.json()
    assert published["warnings"] == ["Email is detected"]

    body = await search_messages(search_client, "searchable")
    assert body["total_count"] == 1
    assert body["results"][0]["id"] == published["message_id"]


@pytest.mark.asyncio
async def test_duplicate_publish_returns_conflict(message_client):
    payload = {"text": "Duplicate integration message", "references": []}

    first = await message_client.post("/messages/publish", json=payload)
    duplicate = await message_client.post("/messages/publish", json=payload)

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Duplicate detected"


@pytest.mark.asyncio
async def test_hide_removes_message_from_search(message_client, search_client):
    published = await publish_message(message_client, "Hide visibility token")

    hide_response = await message_client.post(f"/messages/{published['message_id']}/hide")
    body = await search_messages(search_client, "visibility")

    assert hide_response.status_code == 200
    assert hide_response.json() == {"status": "hidden"}
    assert body["total_count"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_erase_hides_message_and_detaches_author(message_client, search_client, db_session):
    author_id = str(uuid4())
    published = await publish_message(message_client, "Erase visibility token", author_id=author_id)

    erase_response = await message_client.post(f"/messages/{published['message_id']}/erase")
    body = await search_messages(search_client, "visibility")
    result = await db_session.execute(
        select(MessageModel).where(MessageModel.id == UUID(published["message_id"]))
    )
    model = result.scalar_one()

    assert erase_response.status_code == 200
    assert erase_response.json() == {"status": "erased"}
    assert body["total_count"] == 0
    assert model.hidden is True
    assert model.author_id is None


@pytest.mark.asyncio
async def test_search_writes_log_entry(message_client, search_client, db_session):
    await publish_message(message_client, "Loggable search target")

    body = await search_messages(search_client, "loggable")
    result = await db_session.execute(select(SearchLogModel))
    logs = result.scalars().all()

    assert body["total_count"] == 1
    assert len(logs) == 1
    assert logs[0].query_string == "loggable"
    assert logs[0].results_count == 1


@pytest.mark.asyncio
async def test_empty_search_query_returns_bad_request(search_client):
    response = await search_client.get("/search/messages", params={"query_string": ""})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_too_long_search_query_returns_bad_request(search_client):
    response = await search_client.get("/search/messages", params={"query_string": "x" * 251})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_special_character_search_query_does_not_fail(message_client, search_client):
    published = await publish_message(message_client, "Special symbols searchable target")

    body = await search_messages(search_client, "searchable !@#$%^&*()")

    assert body["total_count"] == 1
    assert body["results"][0]["id"] == published["message_id"]
