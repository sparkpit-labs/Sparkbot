from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


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


def test_round_table_status_describes_local_rooms() -> None:
    client = TestClient(app)
    response = client.get("/round-table/status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "available"
    assert payload["meeting_engine"] == "local-rooms"
    assert payload["agent_orchestration"] == "runner-on-this-computer"
    assert payload["model_calls"] == "none-in-sparkbot"
    assert payload["turn_persistence"] == "local-sqlite"
    assert payload["rooms_api"] == "/roundtable/rooms"
    assert [seat["id"] for seat in payload["seats"]] == ["owner", "agent", "guest"]


def test_round_table_seat_statuses_are_contract_values() -> None:
    client = TestClient(app)
    seats = {seat["id"]: seat for seat in client.get("/round-table/status").json()["seats"]}

    assert {seat["status"] for seat in seats.values()} <= ALLOWED_CAPABILITY_STATUSES
    assert seats["owner"]["status"] == "available"
    assert seats["agent"]["status"] == "available"
    # Guests from other devices are not built yet; the status must say so.
    assert seats["guest"]["status"] == "planned"


def test_round_table_status_contains_no_secret_fields() -> None:
    client = TestClient(app)
    payload = client.get("/round-table/status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)


def test_round_table_status_is_read_only() -> None:
    client = TestClient(app)

    for method_name in ["post", "put", "patch", "delete"]:
        response = getattr(client, method_name)("/round-table/status")
        assert response.status_code == 405

    # The working API lives under /roundtable and is owner- or seat-guarded.
    assert client.get("/round-table/start").status_code == 404
    assert client.get("/round-table/run").status_code == 404
