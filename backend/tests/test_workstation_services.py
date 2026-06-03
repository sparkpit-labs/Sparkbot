from fastapi.testclient import TestClient

from app.main import app


def test_workstation_state_and_seat_persistence(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    state_response = client.get("/api/workstation/state")
    assert state_response.status_code == 200
    state = state_response.json()
    assert state["storage"]["type"] == "sqlite"
    assert len(state["seats"]) == 8
    assert "secrets" not in str(state).lower()

    update_response = client.patch(
        "/api/seats/1",
        json={"agent": "analyst", "provider": "openai", "model": "gpt-4o-mini"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["agent"] == "analyst"

    second_client = TestClient(app)
    persisted_response = second_client.get("/api/seats")
    assert persisted_response.status_code == 200
    assert persisted_response.json()["seats"][0]["model"] == "gpt-4o-mini"


def test_room_create_list_read_and_event(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/rooms",
        json={"title": "Planning Room", "goal": "Plan the next Workstation slice", "phase": "setup"},
    )
    assert create_response.status_code == 201
    room = create_response.json()
    assert room["title"] == "Planning Room"
    assert len(room["participants"]) == 8

    list_response = client.get("/api/rooms")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1

    read_response = client.get(f"/api/rooms/{room['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["goal"] == "Plan the next Workstation slice"

    events_response = client.get("/api/events?event_type=room.created")
    assert events_response.status_code == 200
    assert events_response.json()["count"] == 1


def test_note_create_update_list(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/notes",
        json={"title": "Manager summary", "body": "Seat 1 will summarize here.", "surface": "room", "source_id": "room-1", "tags": ["summary"]},
    )
    assert create_response.status_code == 201
    note = create_response.json()
    assert note["tags"] == ["summary"]

    update_response = client.patch(f"/api/notes/{note['id']}", json={"body": "Updated summary."})
    assert update_response.status_code == 200
    assert update_response.json()["body"] == "Updated summary."

    list_response = client.get("/api/notes?surface=room&source_id=room-1")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1


def test_memory_create_list_recall_delete(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/memory",
        json={"content": "The user prefers concise meeting plans.", "memory_type": "preference", "source_surface": "chat", "source_id": "chat-1", "tags": ["meetings"]},
    )
    assert create_response.status_code == 201
    memory = create_response.json()
    assert memory["source_surface"] == "chat"

    list_response = client.get("/api/memory")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1

    recall_response = client.post("/api/memory/recall", json={"query": "concise meeting", "limit": 5})
    assert recall_response.status_code == 200
    assert recall_response.json()["count"] == 1

    delete_response = client.delete(f"/api/memory/{memory['id']}")
    assert delete_response.status_code == 200

    recall_after_delete = client.post("/api/memory/recall", json={"query": "concise meeting", "limit": 5})
    assert recall_after_delete.status_code == 200
    assert recall_after_delete.json()["count"] == 0


def test_event_append_list_and_confirmation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    event_response = client.post(
        "/api/events",
        json={"event_type": "workstation.test", "surface": "tests", "summary": "Manual event", "payload": {"ok": True, "api_key": "example-value", "nested": {"token": "example-token"}}},
    )
    assert event_response.status_code == 201

    confirmation_response = client.post(
        "/api/guardian/actions/confirmations",
        json={"action_type": "note.delete", "prompt": "Confirm note delete", "surface": "notes"},
    )
    assert confirmation_response.status_code == 201
    assert confirmation_response.json()["status"] == "pending"

    events_response = client.get("/api/events")
    assert events_response.status_code == 200
    event_types = {event["event_type"] for event in events_response.json()["events"]}
    assert "workstation.test" in event_types
    manual_event = next(event for event in events_response.json()["events"] if event["event_type"] == "workstation.test")
    assert manual_event["payload"]["api_key"] == "[redacted]"
    assert manual_event["payload"]["nested"]["token"] == "[redacted]"
    assert "guardian.confirmation_required" in event_types

    dashboard_response = client.get("/api/v1/chat/dashboard/summary")
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["summary"]["pending_approvals"] == 1
