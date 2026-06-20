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


def test_model_seats_status_is_static_preview() -> None:
    client = TestClient(app)
    response = client.get("/model-seats/status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "preview"
    assert payload["model_calls"] == "not-implemented"
    assert payload["model_routing"] == "not-implemented"
    assert payload["provider_credentials"] == "not-implemented"
    assert payload["seat_persistence"] == "not-implemented"
    assert payload["seats"] == [
        {
            "id": "default-assistant",
            "label": "Default Assistant Seat",
            "status": "preview",
            "notes": "Read-only seat preview. No model is assigned or called.",
        },
        {
            "id": "research-seat",
            "label": "Research Seat",
            "status": "planned",
            "notes": "Future seat for research workflows. No runtime behavior is implemented.",
        },
        {
            "id": "builder-seat",
            "label": "Builder Seat",
            "status": "planned",
            "notes": "Future seat for implementation workflows. No tool execution is implemented.",
        },
        {
            "id": "reviewer-seat",
            "label": "Reviewer Seat",
            "status": "planned",
            "notes": "Future seat for review workflows. No model routing is implemented.",
        },
    ]


def test_model_seats_remain_non_runtime_contract_values() -> None:
    client = TestClient(app)
    payload = client.get("/model-seats/status").json()
    seats = _seat_by_id(payload)

    assert {seat["status"] for seat in payload["seats"]} <= ALLOWED_CAPABILITY_STATUSES
    assert all(seat["status"] != "available" for seat in payload["seats"])
    assert seats["default-assistant"]["status"] == "preview"
    assert seats["research-seat"]["status"] == "planned"
    assert seats["builder-seat"]["status"] == "planned"
    assert seats["reviewer-seat"]["status"] == "planned"


def test_model_seats_status_contains_no_secret_fields() -> None:
    client = TestClient(app)
    payload = client.get("/model-seats/status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)

    assert payload["model_calls"] == "not-implemented"
    assert payload["model_routing"] == "not-implemented"
    assert payload["provider_credentials"] == "not-implemented"
    assert payload["seat_persistence"] == "not-implemented"


def test_model_seats_status_does_not_claim_active_runtime() -> None:
    client = TestClient(app)
    payload = client.get("/model-seats/status").json()
    serialized = str(payload).lower()

    assert "available" not in serialized
    assert "model calls enabled" not in serialized
    assert "model routing enabled" not in serialized
    assert "provider credentials configured" not in serialized
    assert "seat persistence enabled" not in serialized
    assert "assigned model" not in serialized


def test_no_model_seat_runtime_endpoint_was_introduced() -> None:
    client = TestClient(app)

    for method_name in ["post", "put", "patch", "delete"]:
        method = getattr(client, method_name)
        response = method("/model-seats/status")
        assert response.status_code == 405

    assert client.get("/model-seats/assign").status_code == 404
    assert client.get("/model-seats/save").status_code == 404
    assert client.get("/model-seats/test").status_code == 404
    assert client.get("/model-seats/call").status_code == 404
