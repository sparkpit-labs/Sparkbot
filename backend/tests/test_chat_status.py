from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


def _surface_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {surface["id"]: surface for surface in payload["supported_surfaces"]}


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


def test_chat_status_is_static_preview() -> None:
    client = TestClient(app)
    response = client.get("/chat/status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "preview"
    assert payload["chat_runtime"] == "not-implemented"
    assert payload["message_persistence"] == "not-implemented"
    assert payload["model_calls"] == "not-implemented"
    assert payload["streaming"] == "not-implemented"
    assert payload["provider_routing"] == "not-implemented"
    assert payload["supported_surfaces"] == [
        {
            "id": "chat-shell",
            "label": "Chat shell",
            "status": "preview",
            "notes": "Static chat shell preview. No messages are sent.",
        },
        {
            "id": "message-input",
            "label": "Message input",
            "status": "disabled-by-default",
            "notes": "Input remains disabled until chat runtime and safety gates exist.",
        },
        {
            "id": "model-response",
            "label": "Model response",
            "status": "guarded-future",
            "notes": "No model calls are implemented.",
        },
        {
            "id": "message-history",
            "label": "Message history",
            "status": "guarded-future",
            "notes": "No message persistence is implemented.",
        },
    ]


def test_chat_surfaces_remain_non_runtime_contract_values() -> None:
    client = TestClient(app)
    payload = client.get("/chat/status").json()
    surfaces = _surface_by_id(payload)

    assert {surface["status"] for surface in payload["supported_surfaces"]} <= ALLOWED_CAPABILITY_STATUSES
    assert all(surface["status"] != "available" for surface in payload["supported_surfaces"])
    assert surfaces["chat-shell"]["status"] == "preview"
    assert surfaces["message-input"]["status"] == "disabled-by-default"
    assert surfaces["model-response"]["status"] == "guarded-future"
    assert surfaces["message-history"]["status"] == "guarded-future"


def test_chat_status_contains_no_secret_fields() -> None:
    client = TestClient(app)
    payload = client.get("/chat/status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)

    assert payload["chat_runtime"] == "not-implemented"
    assert payload["message_persistence"] == "not-implemented"
    assert payload["model_calls"] == "not-implemented"
    assert payload["streaming"] == "not-implemented"
    assert payload["provider_routing"] == "not-implemented"


def test_chat_status_does_not_claim_active_runtime() -> None:
    client = TestClient(app)
    payload = client.get("/chat/status").json()
    serialized = str(payload).lower()

    assert "available" not in serialized
    assert "chat runtime active" not in serialized
    assert "message persistence enabled" not in serialized
    assert "model calls enabled" not in serialized
    assert "streaming enabled" not in serialized
    assert "provider routing enabled" not in serialized
    assert "send enabled" not in serialized


def test_no_chat_runtime_endpoint_was_introduced() -> None:
    client = TestClient(app)

    for method_name in ["post", "put", "patch", "delete"]:
        method = getattr(client, method_name)
        response = method("/chat/status")
        assert response.status_code == 405

    assert client.get("/chat/send").status_code == 404
    assert client.post("/chat/send").status_code == 404
    assert client.get("/chat/messages").status_code == 404
    assert client.post("/chat/messages").status_code == 404
    assert client.get("/chat/stream").status_code == 404
