import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import app
from app.services.local_workstation_store import LocalWorkstationStore


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    return TestClient(app)


def _walk_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        keys = list(value.keys())
        for child in value.values():
            keys.extend(_walk_keys(child))
        return keys
    if isinstance(value, list):
        keys: list[str] = []
        for child in value:
            keys.extend(_walk_keys(child))
        return keys
    return []


def _assert_no_credential_fields(payload: Mapping[str, Any]) -> None:
    blocked = ("api_key", "apikey", "password", "token", "secret")
    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in blocked)


def test_store_initializes_in_configured_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))

    store = LocalWorkstationStore()

    assert store.data_dir == tmp_path
    assert store.database_path == tmp_path / "sparkbot_public.sqlite3"
    assert store.database_path.exists()
    assert Path.cwd() not in store.database_path.parents


def test_local_chat_session_and_messages_crud(client: TestClient) -> None:
    created = client.post("/local/chat/sessions", json={"title": "Local planning"})
    assert created.status_code == 201
    session = created.json()
    _assert_no_credential_fields(session)
    assert session["title"] == "Local planning"
    assert session["messages"] == []

    listed = client.get("/local/chat/sessions")
    assert listed.status_code == 200
    assert listed.json()["sessions"][0]["id"] == session["id"]
    assert listed.json()["sessions"][0]["message_count"] == 0

    message = client.post(
        f"/local/chat/sessions/{session['id']}/messages",
        json={"role": "operator", "content": "Keep this note local."},
    )
    assert message.status_code == 201
    assert message.json()["role"] == "operator"
    assert message.json()["content"] == "Keep this note local."

    fetched = client.get(f"/local/chat/sessions/{session['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["messages"] == [message.json()]

    updated = client.patch(f"/local/chat/sessions/{session['id']}", json={"title": "Updated local planning"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated local planning"

    deleted = client.delete(f"/local/chat/sessions/{session['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/local/chat/sessions/{session['id']}").status_code == 404


def test_chat_delete_cleans_messages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    created = client.post("/local/chat/sessions", json={"title": "Cascade check"}).json()
    client.post(f"/local/chat/sessions/{created['id']}/messages", json={"role": "note", "content": "local only"})

    assert client.delete(f"/local/chat/sessions/{created['id']}").status_code == 204

    store = LocalWorkstationStore(tmp_path)
    with store.connect() as connection:
        count = connection.execute("SELECT COUNT(*) AS count FROM chat_messages").fetchone()["count"]
    assert count == 0


def test_memory_notes_crud_and_persistence(client: TestClient, tmp_path: Path) -> None:
    created = client.post("/local/memory-notes", json={"title": "Local note", "body": "Remember locally."})
    assert created.status_code == 201
    note = created.json()
    _assert_no_credential_fields(note)
    assert note["source"] == "operator"

    assert client.get("/local/memory-notes").json()["notes"][0]["id"] == note["id"]
    assert client.get(f"/local/memory-notes/{note['id']}").json()["body"] == "Remember locally."

    updated = client.patch(f"/local/memory-notes/{note['id']}", json={"body": "Updated local note."})
    assert updated.status_code == 200
    assert updated.json()["body"] == "Updated local note."

    second_store = LocalWorkstationStore(tmp_path)
    assert second_store.get_memory_note(note["id"])["body"] == "Updated local note."

    assert client.delete(f"/local/memory-notes/{note['id']}").status_code == 204
    assert client.get(f"/local/memory-notes/{note['id']}").status_code == 404


def test_work_lane_cards_crud_and_validation(client: TestClient, tmp_path: Path) -> None:
    created = client.post(
        "/local/work-lane-cards",
        json={"lane": "inbox", "title": "Draft task", "body": "Plan locally.", "status": "open"},
    )
    assert created.status_code == 201
    card = created.json()
    _assert_no_credential_fields(card)
    assert card["lane"] == "inbox"
    assert card["status"] == "open"

    listed = client.get("/local/work-lane-cards")
    assert listed.status_code == 200
    assert listed.json()["cards"][0]["id"] == card["id"]

    updated = client.patch(f"/local/work-lane-cards/{card['id']}", json={"lane": "active", "status": "in-progress"})
    assert updated.status_code == 200
    assert updated.json()["lane"] == "active"
    assert updated.json()["status"] == "in-progress"

    second_store = LocalWorkstationStore(tmp_path)
    assert second_store.get_work_lane_card(card["id"])["lane"] == "active"

    assert client.post("/local/work-lane-cards", json={"lane": "queued", "title": "Bad", "body": "Bad"}).status_code == 422
    assert client.post(
        "/local/work-lane-cards",
        json={"lane": "inbox", "title": "Bad", "body": "Bad", "status": "waiting"},
    ).status_code == 422

    assert client.delete(f"/local/work-lane-cards/{card['id']}").status_code == 204
    assert client.get(f"/local/work-lane-cards/{card['id']}").status_code == 404


def test_local_runtime_does_not_add_model_provider_or_execution_paths(client: TestClient) -> None:
    route_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    forbidden_paths = {
        "/local/chat/send",
        "/local/chat/stream",
        "/local/model-call",
        "/local/provider-call",
        "/local/connector-call",
        "/local/work-lane-cards/{card_id}/execute",
        "/local/work-lane-cards/{card_id}/schedule",
    }

    assert route_paths.isdisjoint(forbidden_paths)
    assert client.post("/local/chat/send", json={}).status_code == 404
    assert client.post("/local/chat/stream", json={}).status_code == 404
    assert client.post("/local/model-call", json={}).status_code == 404
    assert client.post("/local/provider-call", json={}).status_code == 404
    assert client.post("/local/connector-call", json={}).status_code == 404


def test_existing_status_endpoints_still_pass(client: TestClient) -> None:
    for path in [
        "/health",
        "/capabilities",
        "/provider-config/status",
        "/connector-status",
        "/guardian/status",
        "/round-table/status",
        "/chat/status",
        "/model-seats/status",
        "/work-lanes/status",
    ]:
        response = client.get(path)
        assert response.status_code == 200
