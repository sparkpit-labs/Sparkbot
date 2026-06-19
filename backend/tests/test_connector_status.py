from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


def _connector_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {connector["id"]: connector for connector in payload["connectors"]}


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


def test_connector_status_is_static_guarded_future() -> None:
    client = TestClient(app)
    response = client.get("/connector-status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "guarded-future"
    assert payload["connectors_enabled"] is False
    assert payload["outbound_actions"] == "not-implemented"
    assert payload["credential_storage"] == "not-implemented"
    assert payload["audit_trail"] == "planned"
    assert payload["connectors"] == [
        {
            "id": "messaging",
            "label": "Messaging connectors",
            "status": "guarded-future",
            "notes": "Messaging connectors are planned for future guarded configuration. No outbound sends are implemented.",
        },
        {
            "id": "calendar",
            "label": "Calendar connectors",
            "status": "guarded-future",
            "notes": "Calendar connectors are planned for future guarded configuration.",
        },
        {
            "id": "email",
            "label": "Email connectors",
            "status": "guarded-future",
            "notes": "Email connectors are planned for future guarded configuration. No external sends are implemented.",
        },
        {
            "id": "files",
            "label": "File connectors",
            "status": "guarded-future",
            "notes": "File connectors are planned for future guarded configuration. No file mutation is implemented.",
        },
    ]


def test_connector_statuses_remain_non_runtime_contract_values() -> None:
    client = TestClient(app)
    payload = client.get("/connector-status").json()
    connectors = _connector_by_id(payload)

    assert {connector["status"] for connector in payload["connectors"]} <= ALLOWED_CAPABILITY_STATUSES
    assert all(connector["status"] != "available" for connector in payload["connectors"])
    assert all(connector["status"] == "guarded-future" for connector in payload["connectors"])
    assert connectors["messaging"]["status"] == "guarded-future"
    assert connectors["calendar"]["status"] == "guarded-future"
    assert connectors["email"]["status"] == "guarded-future"
    assert connectors["files"]["status"] == "guarded-future"


def test_connector_status_contains_no_secret_fields() -> None:
    client = TestClient(app)
    payload = client.get("/connector-status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)

    assert payload["connectors_enabled"] is False
    assert payload["outbound_actions"] == "not-implemented"
    assert payload["credential_storage"] == "not-implemented"


def test_no_connector_action_endpoint_was_introduced() -> None:
    client = TestClient(app)

    for method_name in ["post", "put", "patch", "delete"]:
        method = getattr(client, method_name)
        response = method("/connector-status")
        assert response.status_code == 405

    assert client.get("/connector-status/send").status_code == 404
    assert client.get("/connector-status/action").status_code == 404
    assert client.get("/connector-status/connect").status_code == 404
