from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.services.workstation_store import get_store


def _create_memory(client: TestClient, content: str = "Boundary memory") -> dict:
    response = client.post(
        "/api/memory",
        json={"content": content, "memory_type": "boundary", "source_surface": "workstation"},
    )
    assert response.status_code == 201
    return response.json()


def _create_confirmation(client: TestClient, memory_id: str, **patch: str) -> dict:
    payload = {
        "action_type": "memory.delete",
        "surface": "memory",
        "source_id": memory_id,
        "prompt": "Confirm memory delete",
    }
    payload.update(patch)
    response = client.post("/api/guardian/actions/confirmations", json=payload)
    assert response.status_code == 201
    return response.json()


def _decide(client: TestClient, confirmation_id: str, decision: str = "approved") -> dict:
    response = client.post(
        f"/api/guardian/actions/confirmations/{confirmation_id}/decision",
        json={"decision": decision},
    )
    assert response.status_code == 200
    return response.json()


def test_guardian_confirmation_persists_and_appears_in_shared_state_and_spine(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    confirmation = client.post(
        "/api/guardian/actions/confirmations",
        json={"action_type": "memory.delete", "surface": "memory", "source_id": "memory-1"},
    ).json()

    second_client = TestClient(app)
    state_response = second_client.get("/api/workstation/state")
    assert state_response.status_code == 200
    state = state_response.json()
    assert state["dashboard"]["pending_confirmations"] == 1
    assert state["guardian"]["pending_confirmations"][0]["id"] == confirmation["id"]

    spine_events_response = second_client.get("/api/v1/chat/spine/operator/events")
    assert spine_events_response.status_code == 200
    event_types = {event["event_type"] for event in spine_events_response.json()["events"]}
    assert "guardian.confirmation_required" in event_types


def test_event_payload_redaction_applies_to_guardian_shared_log(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    event_response = client.post(
        "/api/events",
        json={
            "event_type": "guardian.audit",
            "surface": "guardian",
            "summary": "Audit event",
            "payload": {"api_key": "example-value", "nested": {"credential": "example-credential"}},
        },
    )
    assert event_response.status_code == 201

    events = client.get("/api/v1/chat/spine/operator/events").json()["events"]
    event = next(item for item in events if item["event_type"] == "guardian.audit")
    assert event["payload"]["api_key"] == "[redacted]"
    assert event["payload"]["nested"]["credential"] == "[redacted]"


def test_memory_delete_fails_closed_without_valid_confirmation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)
    memory = _create_memory(client)

    no_confirmation = client.delete(f"/api/memory/{memory['id']}")
    assert no_confirmation.status_code == 403

    malformed = client.delete(f"/api/memory/{memory['id']}?confirmation_id=not-a-real-confirmation")
    assert malformed.status_code == 403

    pending = _create_confirmation(client, memory["id"])
    pending_response = client.delete(f"/api/memory/{memory['id']}?confirmation_id={pending['id']}")
    assert pending_response.status_code == 403

    recall = client.post("/api/memory/recall", json={"query": "Boundary", "limit": 5})
    assert recall.status_code == 200
    assert recall.json()["count"] == 1


def test_denied_confirmation_cannot_authorize_memory_delete(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)
    memory = _create_memory(client)
    confirmation = _create_confirmation(client, memory["id"])
    denied = _decide(client, confirmation["id"], "denied")
    assert denied["status"] == "denied"

    response = client.delete(f"/api/memory/{memory['id']}?confirmation_id={confirmation['id']}")
    assert response.status_code == 403


def test_expired_confirmation_cannot_authorize_memory_delete(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)
    memory = _create_memory(client)
    confirmation = _create_confirmation(client, memory["id"])
    _decide(client, confirmation["id"], "approved")

    expired_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    with get_store().connect() as conn:
        conn.execute(
            "UPDATE action_confirmations SET expires_at = ? WHERE id = ?",
            (expired_at, confirmation["id"]),
        )

    response = client.delete(f"/api/memory/{memory['id']}?confirmation_id={confirmation['id']}")
    assert response.status_code == 403
    stored = client.get("/api/guardian/actions/confirmations?status=expired").json()
    assert stored["count"] == 1


def test_approved_confirmation_is_action_bound_and_one_time_use(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)
    memory = _create_memory(client, "Memory to delete once")
    other_memory = _create_memory(client, "Memory to keep")

    generic = _create_confirmation(client, memory["id"], action_type="workstation.action")
    _decide(client, generic["id"], "approved")
    mismatch_response = client.delete(f"/api/memory/{memory['id']}?confirmation_id={generic['id']}")
    assert mismatch_response.status_code == 403

    wrong_source = _create_confirmation(client, other_memory["id"])
    _decide(client, wrong_source["id"], "approved")
    wrong_source_response = client.delete(f"/api/memory/{memory['id']}?confirmation_id={wrong_source['id']}")
    assert wrong_source_response.status_code == 403

    confirmation = _create_confirmation(client, memory["id"])
    _decide(client, confirmation["id"], "approved")
    delete_response = client.delete(f"/api/memory/{memory['id']}?confirmation_id={confirmation['id']}")
    assert delete_response.status_code == 200

    authorized, reason = get_store().authorize_action(
        confirmation["id"],
        "memory.delete",
        "memory",
        memory["id"],
    )
    assert authorized is False
    assert "already used" in reason

    events = client.get("/api/events").json()["events"]
    event_types = {event["event_type"] for event in events}
    assert "guardian.action_authorized" in event_types
    assert "guardian.action_blocked" in event_types
