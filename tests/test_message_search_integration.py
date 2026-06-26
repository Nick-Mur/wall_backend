import pytest


@pytest.mark.asyncio
async def test_publish_message_then_search_finds_it(message_client, search_client):
    publish_response = await message_client.post(
        "/messages/publish",
        json={
            "text": "Integration searchable message",
            "references": [],
        },
    )

    assert publish_response.status_code == 201
    message_id = publish_response.json()["message_id"]

    search_response = await search_client.get(
        "/search/messages",
        params={"query_string": "searchable"},
    )

    assert search_response.status_code == 200
    body = search_response.json()
    assert body["total_count"] == 1
    assert body["results"][0]["id"] == message_id
    assert "searchable" in body["results"][0]["snippet"].lower()
