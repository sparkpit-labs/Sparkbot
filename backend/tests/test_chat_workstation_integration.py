from fastapi.testclient import TestClient

from app.main import app
from app.services import model_execution


PROVIDER_ENVS = [
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "MINIMAX_API_KEY",
    "XAI_API_KEY",
]


def _clear_provider_env(monkeypatch) -> None:
    for name in PROVIDER_ENVS:
        monkeypatch.delenv(name, raising=False)


def _save_openrouter_credential(client: TestClient, credential: str = "unit-test-credential-value") -> None:
    response = client.post("/api/v1/chat/models/config", json={"providers": {"openrouter_api_key": credential}})
    assert response.status_code == 200


def test_chat_turn_persists_context_memory_and_events(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
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


def test_chat_provider_prompt_uses_recalled_memory_and_notes_safely(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    calls: list[dict[str, object]] = []

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        calls.append({"url": url, "headers": headers, "payload": payload, "timeout": timeout_seconds})
        return {"choices": [{"message": {"content": "Safe chat provider response."}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    memory_response = client.post(
        "/api/memory",
        json={
            "content": "Launch context prefers short answers. api_key=raw-memory-secret",
            "memory_type": "preference",
            "source_surface": "workstation",
            "tags": ["launch"],
        },
    )
    assert memory_response.status_code == 201
    assert memory_response.json()["content"] == "Launch context prefers short answers. api_key=[redacted]"

    note_response = client.post(
        "/api/notes",
        json={"title": "Launch note", "body": "Use the shared plan. token raw-note-secret", "surface": "workstation", "tags": ["launch"]},
    )
    assert note_response.status_code == 201
    assert "raw-note-secret" not in str(note_response.json())

    chat_response = client.post("/api/chat/messages", json={"content": "Use the launch context memory."})

    assert chat_response.status_code == 201
    payload = chat_response.json()
    assert payload["model_execution"]["status"] == "success"
    assert len(calls) == 1
    messages = calls[0]["payload"]["messages"]  # type: ignore[index]
    prompt_text = "\n".join(str(message.get("content") or "") for message in messages)
    assert "Shared Workstation context is redacted and source-labeled" in prompt_text
    assert "Memory/preference [workstation:shared; actor:operator; tags:launch]" in prompt_text
    assert "Launch context prefers short answers. api_key=[redacted]" in prompt_text
    assert "Note/Launch note [workstation:shared; actor:operator; tags:launch]" in prompt_text
    assert "Use the shared plan. token [redacted]" in prompt_text
    assert "raw-memory-secret" not in prompt_text
    assert "raw-note-secret" not in prompt_text

    events = client.get("/api/events?event_type=model.call.completed").json()["events"]
    assert events
    assert all("messages" not in event["payload"] for event in events)
    assert all("prompt" not in event["payload"] for event in events)
    assert all("Safe chat provider response" not in str(event["payload"]) for event in events)
    assert "unit-test-credential-value" not in str(events)
    assert "raw-memory-secret" not in str(payload)
    assert "raw-note-secret" not in str(payload)


def test_chat_memory_delete_request_creates_confirmation_without_deleting(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
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


def test_chat_work_request_dispatches_as_text_without_execution_block(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    calls: list[dict[str, object]] = []

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        calls.append({"url": url, "headers": headers, "payload": payload})
        return {"choices": [{"message": {"content": "Text-only work plan."}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    chat_response = client.post(
        "/api/chat/messages",
        json={"content": "run command to write file for me"},
    )
    assert chat_response.status_code == 201
    payload = chat_response.json()
    assert payload["blocked_action"] is None
    assert payload["model_execution"]["status"] == "success"
    assert payload["assistant_message"]["content"] == "Text-only work plan."
    assert calls

    events = client.get("/api/events").json()["events"]
    assert any(event["event_type"] == "model.call.completed" for event in events)
    assert not any(event["event_type"] == "guardian.action_blocked" for event in events)



def test_workstation_state_aggregates_chat_rooms_notes_memory_events_and_guardian(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    room_response = client.post(
        "/api/rooms",
        json={"title": "Foundation Review", "goal": "Audit shared product state", "phase": "setup"},
    )
    assert room_response.status_code == 201
    room = room_response.json()

    note_response = client.post(
        "/api/notes",
        json={
            "title": "Foundation note",
            "body": "Use the shared store as the source of truth.",
            "surface": "room",
            "source_id": room["id"],
            "tags": ["audit"],
        },
    )
    assert note_response.status_code == 201

    memory_response = client.post(
        "/api/memory",
        json={
            "content": "Foundation audit prefers explicit deferred labels.",
            "memory_type": "preference",
            "source_surface": "workstation",
            "tags": ["audit"],
        },
    )
    assert memory_response.status_code == 201

    chat_response = client.post(
        "/api/chat/messages",
        json={"content": "Use the foundation audit memory.", "save_to_memory": True},
    )
    assert chat_response.status_code == 201
    chat_payload = chat_response.json()

    confirmation_response = client.post(
        "/api/guardian/actions/confirmations",
        json={"action_type": "memory.delete", "surface": "memory", "source_id": memory_response.json()["id"]},
    )
    assert confirmation_response.status_code == 201
    confirmation = confirmation_response.json()

    state = client.get("/api/workstation/state").json()
    assert state["storage"]["type"] == "sqlite"
    assert {item["id"] for item in state["rooms"]} == {room["id"]}
    assert state["dashboard"]["notes_count"] == 1
    assert state["dashboard"]["memory_count"] == 2
    assert state["chat"]["sessions_count"] == 1
    assert state["chat"]["messages_count"] == 2
    assert state["chat"]["sessions"][0]["id"] == chat_payload["session"]["id"]
    assert state["guardian"]["pending_confirmations"][0]["id"] == confirmation["id"]

    event_types = {event["event_type"] for event in state["events"]}
    assert "room.created" in event_types
    assert "note.saved" in event_types
    assert "memory.saved" in event_types
    assert "chat.message.user" in event_types
    assert "chat.context.recalled" in event_types
    assert "guardian.confirmation_required" in event_types


def test_approved_guardian_confirmation_survives_restart_and_is_used_once(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    memory = client.post(
        "/api/memory",
        json={"content": "Restart-safe memory", "memory_type": "audit", "source_surface": "workstation"},
    ).json()
    confirmation = client.post(
        "/api/guardian/actions/confirmations",
        json={"action_type": "memory.delete", "surface": "memory", "source_id": memory["id"]},
    ).json()
    approve_response = client.post(
        f"/api/guardian/actions/confirmations/{confirmation['id']}/decision",
        json={"decision": "approved"},
    )
    assert approve_response.status_code == 200

    second_client = TestClient(app)
    delete_response = second_client.delete(f"/api/memory/{memory['id']}?confirmation_id={confirmation['id']}")
    assert delete_response.status_code == 200

    reuse_response = second_client.delete(f"/api/memory/{memory['id']}?confirmation_id={confirmation['id']}")
    assert reuse_response.status_code == 403

    confirmations = second_client.get("/api/guardian/actions/confirmations?status=used").json()
    assert confirmations["count"] == 1
    recall = second_client.post("/api/memory/recall", json={"query": "Restart-safe", "limit": 5})
    assert recall.status_code == 200
    assert recall.json()["count"] == 0
