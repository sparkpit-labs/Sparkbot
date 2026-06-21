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
    assert card["chat_session_id"] is None
    assert card["linked_chat_session_title"] is None

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


def test_work_lane_card_can_link_and_unlink_local_chat_session(client: TestClient, tmp_path: Path) -> None:
    session = client.post("/local/chat/sessions", json={"title": "Linked local chat"}).json()

    created = client.post(
        "/local/work-lane-cards",
        json={
            "lane": "planned",
            "title": "Linked card",
            "body": "Discuss in local chat.",
            "status": "open",
            "chat_session_id": session["id"],
        },
    )

    assert created.status_code == 201
    card = created.json()
    assert card["chat_session_id"] == session["id"]
    assert card["linked_chat_session_title"] == "Linked local chat"

    listed = client.get("/local/work-lane-cards").json()["cards"]
    assert listed[0]["chat_session_id"] == session["id"]
    assert listed[0]["linked_chat_session_title"] == "Linked local chat"

    fetched = client.get(f"/local/work-lane-cards/{card['id']}").json()
    assert fetched["linked_chat_session_title"] == "Linked local chat"

    unlinked = client.patch(f"/local/work-lane-cards/{card['id']}", json={"chat_session_id": None})
    assert unlinked.status_code == 200
    assert unlinked.json()["chat_session_id"] is None
    assert unlinked.json()["linked_chat_session_title"] is None

    second_store = LocalWorkstationStore(tmp_path)
    assert second_store.get_work_lane_card(card["id"])["chat_session_id"] is None


def test_work_lane_card_rejects_missing_chat_session_link(client: TestClient) -> None:
    created = client.post(
        "/local/work-lane-cards",
        json={
            "lane": "inbox",
            "title": "Bad link",
            "body": "Missing chat session.",
            "status": "open",
            "chat_session_id": "missing-session",
        },
    )

    assert created.status_code == 404
    assert created.json()["detail"] == "Chat session not found"


def test_deleting_chat_session_unlinks_work_lane_cards(client: TestClient) -> None:
    session = client.post("/local/chat/sessions", json={"title": "Temporary local chat"}).json()
    card = client.post(
        "/local/work-lane-cards",
        json={
            "lane": "review",
            "title": "Card with chat",
            "body": "Keep card when chat is removed.",
            "status": "open",
            "chat_session_id": session["id"],
        },
    ).json()

    assert client.delete(f"/local/chat/sessions/{session['id']}").status_code == 204

    fetched = client.get(f"/local/work-lane-cards/{card['id']}").json()
    assert fetched["chat_session_id"] is None
    assert fetched["linked_chat_session_title"] is None
    assert fetched["title"] == "Card with chat"


def test_work_lane_chat_link_does_not_add_execution_paths(client: TestClient) -> None:
    assert client.post("/local/work-lane-cards/card-1/run", json={}).status_code == 404
    assert client.post("/local/work-lane-cards/card-1/remind", json={}).status_code == 404
    assert client.post("/local/work-lane-cards/card-1/background-job", json={}).status_code == 404


def test_local_export_returns_read_only_workstation_snapshot(client: TestClient) -> None:
    session = client.post("/local/chat/sessions", json={"title": "Export chat"}).json()
    message = client.post(
        f"/local/chat/sessions/{session['id']}/messages",
        json={"role": "operator", "content": "Export this locally."},
    ).json()
    note = client.post("/local/memory-notes", json={"title": "Export note", "body": "Backup this note."}).json()
    card = client.post(
        "/local/work-lane-cards",
        json={
            "lane": "planned",
            "title": "Export card",
            "body": "Backup this card.",
            "status": "open",
            "chat_session_id": session["id"],
        },
    ).json()

    response = client.get("/local/export")

    assert response.status_code == 200
    payload = response.json()
    _assert_no_credential_fields(payload)
    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["export_type"] == "local-workstation-data"
    assert payload["schema_version"] == 1
    assert payload["import_supported"] is False
    assert payload["cloud_sync"] == "not-supported"
    assert payload["external_upload"] == "not-supported"
    assert payload["data"]["chat_sessions"][0]["id"] == session["id"]
    assert payload["data"]["chat_sessions"][0]["messages"] == [message]
    assert payload["data"]["memory_notes"][0]["id"] == note["id"]
    assert payload["data"]["work_lane_cards"][0]["id"] == card["id"]
    assert payload["data"]["work_lane_cards"][0]["linked_chat_session_title"] == "Export chat"

    assert client.get(f"/local/chat/sessions/{session['id']}").status_code == 200
    assert client.get(f"/local/memory-notes/{note['id']}").status_code == 200
    assert client.get(f"/local/work-lane-cards/{card['id']}").status_code == 200


def test_local_runtime_settings_reports_env_driven_local_status(client: TestClient, tmp_path: Path) -> None:
    response = client.get("/local/runtime/settings")

    assert response.status_code == 200
    payload = response.json()
    _assert_no_credential_fields(payload)
    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "available"
    assert payload["configuration"] == "env-driven"
    assert payload["settings_writes"] == "not-supported"
    assert payload["credentials"] == "not-supported"
    assert payload["data_directory"] == {
        "configured_by": "SPARKBOT_DATA_DIR",
        "display_path": str(tmp_path),
    }
    assert payload["sqlite_database"] == {
        "filename": "sparkbot_public.sqlite3",
        "display_path": str(tmp_path / "sparkbot_public.sqlite3"),
    }
    assert payload["local_models"]["enabled"] is False
    assert payload["local_models"]["adapter"] == "ollama"
    assert payload["local_models"]["base_url"] == "http://127.0.0.1:11434"
    assert payload["local_models"]["base_url_policy"] == "localhost-only"
    assert payload["local_models"]["configured_model"] is None
    assert payload["local_models"]["prompt_calls"] == "disabled"


def test_local_runtime_settings_reflects_enabled_ollama_config(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "true")
    monkeypatch.setenv("SPARKBOT_OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("SPARKBOT_OLLAMA_MODEL", "llama3.2")

    def fake_request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 2) -> dict[str, Any]:
        assert url == "http://localhost:11434/api/tags"
        assert payload is None
        return {"models": []}

    from app.services import local_model_adapter

    monkeypatch.setattr(local_model_adapter, "_request_json", fake_request_json)

    payload = client.get("/local/runtime/settings").json()

    assert payload["local_models"]["enabled"] is True
    assert payload["local_models"]["status"] == "available-local-only"
    assert payload["local_models"]["base_url"] == "http://localhost:11434"
    assert payload["local_models"]["configured_model"] == "llama3.2"
    assert payload["local_models"]["prompt_calls"] == "enabled-local-only"


def test_local_runtime_settings_does_not_add_save_secret_or_upload_paths(client: TestClient) -> None:
    route_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    forbidden_paths = {
        "/local/runtime/settings/save",
        "/local/runtime/settings/secrets",
        "/local/runtime/settings/credentials",
        "/local/runtime/settings/upload",
    }

    assert route_paths.isdisjoint(forbidden_paths)
    assert client.post("/local/runtime/settings", json={}).status_code == 405
    for path in forbidden_paths:
        assert client.post(path, json={}).status_code == 404


def test_local_export_does_not_add_import_sync_or_upload_paths(client: TestClient) -> None:
    route_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    forbidden_paths = {
        "/local/import",
        "/local/export/upload",
        "/local/sync",
        "/local/cloud-sync",
        "/local/backup/upload",
    }

    assert route_paths.isdisjoint(forbidden_paths)
    for path in forbidden_paths:
        assert client.post(path, json={}).status_code == 404


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
