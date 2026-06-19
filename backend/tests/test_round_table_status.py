from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


def _seat_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {seat["id"]: seat for seat in payload["seats"]}


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


def test_round_table_status_is_static_preview() -> None:
    client = TestClient(app)
    response = client.get("/round-table/status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "preview"
    assert payload["meeting_engine"] == "not-implemented"
    assert payload["agent_orchestration"] == "not-implemented"
    assert payload["model_calls"] == "not-implemented"
    assert payload["turn_persistence"] == "not-implemented"
    assert payload["seats"] == [
        {
            "id": "operator",
            "label": "Operator",
            "status": "preview",
            "notes": "Human operator role shown as part of the shell preview.",
        },
        {
            "id": "assistant",
            "label": "Assistant seat",
            "status": "preview",
            "notes": "Assistant role preview only. No model calls are made.",
        },
        {
            "id": "research",
            "label": "Research seat",
            "status": "planned",
            "notes": "Research role is planned. No agent runtime is implemented.",
        },
        {
            "id": "builder",
            "label": "Builder seat",
            "status": "planned",
            "notes": "Builder role is planned. No tool execution is implemented.",
        },
        {
            "id": "reviewer",
            "label": "Reviewer seat",
            "status": "planned",
            "notes": "Reviewer role is planned. No review workflow runtime is implemented.",
        },
    ]


def test_round_table_seats_remain_non_runtime_contract_values() -> None:
    client = TestClient(app)
    payload = client.get("/round-table/status").json()
    seats = _seat_by_id(payload)

    assert {seat["status"] for seat in payload["seats"]} <= ALLOWED_CAPABILITY_STATUSES
    assert all(seat["status"] != "available" for seat in payload["seats"])
    assert seats["operator"]["status"] == "preview"
    assert seats["assistant"]["status"] == "preview"
    assert seats["research"]["status"] == "planned"
    assert seats["builder"]["status"] == "planned"
    assert seats["reviewer"]["status"] == "planned"


def test_round_table_status_contains_no_secret_fields() -> None:
    client = TestClient(app)
    payload = client.get("/round-table/status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)

    assert payload["meeting_engine"] == "not-implemented"
    assert payload["agent_orchestration"] == "not-implemented"
    assert payload["model_calls"] == "not-implemented"
    assert payload["turn_persistence"] == "not-implemented"


def test_round_table_status_does_not_claim_active_runtime() -> None:
    client = TestClient(app)
    payload = client.get("/round-table/status").json()
    serialized = str(payload).lower()

    assert "available" not in serialized
    assert "meeting engine active" not in serialized
    assert "agent orchestration active" not in serialized
    assert "model calls enabled" not in serialized
    assert "turn persistence enabled" not in serialized


def test_no_round_table_runtime_endpoint_was_introduced() -> None:
    client = TestClient(app)

    for method_name in ["post", "put", "patch", "delete"]:
        method = getattr(client, method_name)
        response = method("/round-table/status")
        assert response.status_code == 405

    assert client.get("/round-table/start").status_code == 404
    assert client.get("/round-table/invite").status_code == 404
    assert client.get("/round-table/run").status_code == 404
    assert client.get("/round-table/turn").status_code == 404
