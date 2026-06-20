from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


def _lane_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {lane["id"]: lane for lane in payload["lanes"]}


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


def test_task_lanes_status_is_static_preview() -> None:
    client = TestClient(app)
    response = client.get("/work-lanes/status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "preview"
    assert payload["task_runtime"] == "not-implemented"
    assert payload["task_persistence"] == "not-implemented"
    assert payload["scheduler"] == "not-implemented"
    assert payload["background_jobs"] == "not-implemented"
    assert payload["notifications"] == "not-implemented"
    assert payload["lanes"] == [
        {
            "id": "inbox",
            "label": "Inbox Lane",
            "status": "preview",
            "notes": "Read-only lane preview. No tasks are stored or executed.",
        },
        {
            "id": "planned",
            "label": "Planned Lane",
            "status": "planned",
            "notes": "Future planning lane. No scheduler is implemented.",
        },
        {
            "id": "active",
            "label": "Active Lane",
            "status": "planned",
            "notes": "Future active work lane. No task runtime is implemented.",
        },
        {
            "id": "review",
            "label": "Review Lane",
            "status": "planned",
            "notes": "Future review lane. No workflow runtime is implemented.",
        },
    ]


def test_task_lanes_remain_non_runtime_contract_values() -> None:
    client = TestClient(app)
    payload = client.get("/work-lanes/status").json()
    lanes = _lane_by_id(payload)

    assert {lane["status"] for lane in payload["lanes"]} <= ALLOWED_CAPABILITY_STATUSES
    assert all(lane["status"] != "available" for lane in payload["lanes"])
    assert lanes["inbox"]["status"] == "preview"
    assert lanes["planned"]["status"] == "planned"
    assert lanes["active"]["status"] == "planned"
    assert lanes["review"]["status"] == "planned"


def test_task_lanes_status_contains_no_secret_fields() -> None:
    client = TestClient(app)
    payload = client.get("/work-lanes/status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)

    assert payload["task_runtime"] == "not-implemented"
    assert payload["task_persistence"] == "not-implemented"
    assert payload["scheduler"] == "not-implemented"
    assert payload["background_jobs"] == "not-implemented"
    assert payload["notifications"] == "not-implemented"


def test_task_lanes_status_does_not_claim_active_runtime() -> None:
    client = TestClient(app)
    payload = client.get("/work-lanes/status").json()
    serialized = str(payload).lower()

    assert "available" not in serialized
    assert "scheduler enabled" not in serialized
    assert "background jobs enabled" not in serialized
    assert "task runtime enabled" not in serialized
    assert "task persistence enabled" not in serialized
    assert "notifications enabled" not in serialized
    assert "stored task" not in serialized
    assert "executed task" not in serialized


def test_no_task_lane_runtime_endpoint_was_introduced() -> None:
    client = TestClient(app)

    for method_name in ["post", "put", "patch", "delete"]:
        method = getattr(client, method_name)
        response = method("/work-lanes/status")
        assert response.status_code == 405

    assert client.get("/work-lanes/create").status_code == 404
    assert client.get("/work-lanes/update").status_code == 404
    assert client.get("/work-lanes/execute").status_code == 404
    assert client.get("/work-lanes/schedule").status_code == 404
