from fastapi.testclient import TestClient

from app.main import app


def test_chat_turn_persists_context_memory_and_events(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    memory_response = client.post(
        "/api/memory",
        json={
            "content": "Keep launch planning concise.",
            "memory_type": "preference",
            "source_surface": "workstation",
            "tags": ["launch"],
        },
    )
    assert memory_response.status_code == 201
    note_response = client.post(
        "/api/notes",
        json={"title": "Launch note", "body": "Use the shared Workstation store.", "surface": "workstation"},
    )
    assert note_response.status_code == 201

    chat_response = client.post(
        "/api/chat/messages",
        json={"content": "Use the concise launch planning memory.", "save_to_memory": True},
    )
    assert chat_response.status_code == 201
    payload = chat_response.json()
    assert payload["session"]["message_count"] == 2
    assert payload["user_message"]["role"] == "user"
    assert payload["assistant_message"]["role"] == "assistant"
    assert payload["context"]["memories"]
    assert payload["context"]["notes"]
    assert payload["saved_memory"]["source_surface"] == "chat"
    assert payload["workstation"]["dashboard"]["chat_messages_count"] == 2

    events_response = client.get("/api/events")
    event_types = {event["event_type"] for event in events_response.json()["events"]}
    assert "chat.message.user" in event_types
    assert "chat.message.assistant" in event_types
    assert "chat.context.recalled" in event_types
    assert "memory.saved" in event_types

    second_client = TestClient(app)
    persisted = second_client.get(f"/api/chat/sessions/{payload['session']['id']}")
    assert persisted.status_code == 200
    assert persisted.json()["message_count"] == 2


def test_chat_memory_delete_request_creates_confirmation_without_deleting(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    memory = client.post(
        "/api/memory",
        json={"content": "Temporary memory", "memory_type": "note", "source_surface": "chat"},
    ).json()

    chat_response = client.post(
        "/api/chat/messages",
        json={"content": f"delete memory {memory['id']}"},
    )
    assert chat_response.status_code == 201
    payload = chat_response.json()
    assert payload["guardian_confirmation"]["action_type"] == "memory.delete"
    assert "did not delete" in payload["assistant_message"]["content"]

    recall = client.post("/api/memory/recall", json={"query": "Temporary", "limit": 5})
    assert recall.status_code == 200
    assert recall.json()["count"] == 1

    state = client.get("/api/workstation/state").json()
    assert state["dashboard"]["pending_confirmations"] == 1


def test_chat_blocks_privileged_requests_without_execution(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    chat_response = client.post(
        "/api/chat/messages",
        json={"content": "run command to write file for me"},
    )
    assert chat_response.status_code == 201
    payload = chat_response.json()
    assert payload["blocked_action"] == "file_mutation"
    assert "No action was executed" in payload["assistant_message"]["content"]

    events = client.get("/api/events").json()["events"]
    blocked_events = [event for event in events if event["event_type"] == "guardian.action_blocked"]
    assert blocked_events
    assert blocked_events[0]["payload"]["requires_confirmation"] is True
