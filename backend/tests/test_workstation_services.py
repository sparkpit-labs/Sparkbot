from fastapi.testclient import TestClient

from app.main import app


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

    update_response = client.patch(
        f"/api/memory/{memory['id']}",
        json={"content": "The user prefers concise meeting plans. credential raw-memory-marker", "tags": ["meetings", "updated"]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["content"] == "The user prefers concise meeting plans. credential [redacted]"
    assert update_response.json()["tags"] == ["meetings", "updated"]
    assert "raw-memory-marker" not in str(update_response.json())

    confirmation_response = client.post(
        "/api/guardian/actions/confirmations",
        json={
            "action_type": "memory.delete",
            "surface": "memory",
            "source_id": memory["id"],
            "prompt": "Confirm memory delete",
        },
    )
    assert confirmation_response.status_code == 201
    confirmation = confirmation_response.json()
    approval_response = client.post(
        f"/api/guardian/actions/confirmations/{confirmation['id']}/decision",
        json={"decision": "approved"},
    )
    assert approval_response.status_code == 200

    delete_response = client.delete(f"/api/memory/{memory['id']}?confirmation_id={confirmation['id']}")
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


def test_workstation_history_links_notes_sessions_and_safe_events(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    chat_response = client.post(
        "/api/chat/messages",
        json={"content": "Capture this history note. api_key=chat-marker"},
    )
    assert chat_response.status_code == 201
    chat_payload = chat_response.json()
    chat_session_id = chat_payload["session"]["id"]
    assert "chat-marker" not in str(chat_payload)

    note_response = client.post(
        "/api/notes",
        json={
            "title": "History note",
            "body": "Original note body.",
            "surface": "chat",
            "source_id": chat_session_id,
            "tags": ["history"],
        },
    )
    assert note_response.status_code == 201
    note = note_response.json()

    read_note = client.get(f"/api/notes/{note['id']}")
    assert read_note.status_code == 200
    assert read_note.json()["source_id"] == chat_session_id

    update_note = client.patch(
        f"/api/notes/{note['id']}",
        json={"body": "Updated note body. token note-marker"},
    )
    assert update_note.status_code == 200
    assert update_note.json()["body"] == "Updated note body. token [redacted]"
    assert "note-marker" not in str(update_note.json())

    roundtable_create = client.post(
        "/api/roundtable/sessions",
        json={"title": "History Round Table", "goal": "Review persistent notes and Spine history."},
    )
    assert roundtable_create.status_code == 201
    roundtable_id = roundtable_create.json()["id"]
    run_response = client.post(f"/api/roundtable/sessions/{roundtable_id}/run", json={})
    assert run_response.status_code == 200
    roundtable = run_response.json()
    assert roundtable["status"] == "complete"
    assert len(roundtable["notes"]) == 1
    assert roundtable["summaries"][0]["note_id"] == roundtable["notes"][0]["id"]

    roundtable_notes = client.get(f"/api/notes?surface=roundtable&source_id={roundtable_id}")
    assert roundtable_notes.status_code == 200
    assert roundtable_notes.json()["count"] == 1

    client.post(
        "/api/events",
        json={
            "event_type": "model.call.completed",
            "surface": "chat",
            "source_id": chat_session_id,
            "summary": "Model call completed with safe metadata.",
            "payload": {
                "provider": "unit-test",
                "model": "safe-model",
                "prompt": "raw prompt should not appear",
                "messages": [{"role": "user", "content": "raw message"}],
                "output": "raw model output",
                "headers": {"Authorization": "Bearer raw-token"},
                "api_key": "event-marker",
            },
        },
    )

    filtered_events = client.get("/api/events?surface=chat&event_type=model.call.completed")
    assert filtered_events.status_code == 200
    filtered = filtered_events.json()["events"]
    assert len(filtered) == 1
    assert filtered[0]["payload"]["prompt"] == "[redacted]"
    assert filtered[0]["payload"]["messages"] == "[redacted]"
    assert filtered[0]["payload"]["output"] == "[redacted]"
    assert filtered[0]["payload"]["headers"] == "[redacted]"
    assert filtered[0]["payload"]["api_key"] == "[redacted]"

    history_response = client.get("/api/workstation/history?limit=25")
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["storage"]["type"] == "sqlite"
    assert history["dashboard"]["chat_sessions_count"] == 1
    assert history["dashboard"]["roundtable_sessions_count"] == 1
    assert history["dashboard"]["notes_count"] == 2

    chat_history = history["chat"]["sessions"][0]
    assert chat_history["id"] == chat_session_id
    assert chat_history["message_count"] == 2
    assert chat_history["last_message"]

    roundtable_history = history["roundtable"]["sessions"][0]
    assert roundtable_history["id"] == roundtable_id
    assert roundtable_history["turn_count"] == 16
    assert roundtable_history["assignment_count"] == 7
    assert len(roundtable_history["turns"]) == 16
    assert len(roundtable_history["assignments"]) == 7
    assert len(roundtable_history["summaries"]) == 1
    assert len(roundtable_history["notes"]) == 1
    assert roundtable_history["summaries"][0]["note_id"] == roundtable_history["notes"][0]["id"]

    history_text = str(history)
    assert "chat-marker" not in history_text
    assert "note-marker" not in history_text
    assert "raw prompt should not appear" not in history_text
    assert "raw model output" not in history_text
    assert "event-marker" not in history_text

    second_client = TestClient(app)
    persisted_history = second_client.get("/api/workstation/history?limit=25")
    assert persisted_history.status_code == 200
    persisted_roundtable = persisted_history.json()["roundtable"]["sessions"][0]
    assert persisted_roundtable["turn_count"] == 16
    assert len(persisted_roundtable["notes"]) == 1


def test_task_records_dashboard_spine_and_execution_fail_closed(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/tasks",
        json={
            "title": "Prepare dashboard parity",
            "notes": "Track the local dashboard task. credential work-marker",
            "surface": "room",
            "source_id": "room-1",
            "tags": ["dashboard", "directive"],
            "metadata": {
                "prompt": "raw task prompt",
                "headers": {"Authorization": "Bearer example"},
                "safe": True,
            },
        },
    )
    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]
    assert task["status"] == "open"
    assert task["notes"] == "Track the local dashboard task. credential [redacted]"
    assert task["metadata"]["prompt"] == "[redacted]"
    assert task["metadata"]["headers"] == "[redacted]"
    assert task["execution_enabled"] is False
    assert len(task["history"]) == 1
    assert "work-marker" not in str(task)
    assert "raw task prompt" not in str(task)

    list_response = client.get("/api/tasks?status=open")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["execution_enabled"] is False

    pause_response = client.post(f"/api/tasks/{task_id}/pause", json={})
    assert pause_response.status_code == 200
    assert pause_response.json()["status"] == "paused"

    resume_response = client.post(f"/api/tasks/{task_id}/resume", json={})
    assert resume_response.status_code == 200
    assert resume_response.json()["status"] == "open"

    done_response = client.post(f"/api/tasks/{task_id}/done", json={})
    assert done_response.status_code == 200
    assert done_response.json()["status"] == "done"

    cancel_task = client.post("/api/tasks", json={"title": "Cancel this task", "notes": "Manual state only."})
    assert cancel_task.status_code == 201
    cancel_response = client.post(f"/api/tasks/{cancel_task.json()['id']}/cancel", json={})
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "canceled"

    run_response = client.post(f"/api/tasks/{task_id}/run", json={})
    assert run_response.status_code == 403
    assert "disabled" in run_response.json()["detail"]

    write_response = client.post(f"/api/tasks/{task_id}/write-mode", json={})
    assert write_response.status_code == 403

    read_response = client.get(f"/api/tasks/{task_id}")
    assert read_response.status_code == 200
    history = read_response.json()["history"]
    event_types = [entry["event_type"] for entry in history]
    assert "task.created" in event_types
    assert "task.paused" in event_types
    assert "task.resumed" in event_types
    assert "task.done" in event_types
    assert event_types.count("task.execution_blocked") == 2

    task_history = client.get(f"/api/tasks/{task_id}/history")
    assert task_history.status_code == 200
    assert task_history.json()["count"] == len(history)

    dashboard = client.get("/api/v1/chat/dashboard/summary")
    assert dashboard.status_code == 200
    summary = dashboard.json()["summary"]
    assert summary["tasks_count"] == 2
    assert summary["open_tasks"] == 0
    assert summary["done_tasks_count"] == 1
    assert summary["canceled_tasks_count"] == 1
    assert summary["task_execution_enabled"] is False

    spine = client.get("/api/v1/chat/spine/operator/overview")
    assert spine.status_code == 200
    spine_payload = spine.json()
    assert spine_payload["task_execution_enabled"] is False
    assert len(spine_payload["completed_queue"]) == 1
    assert len(spine_payload["blocked_queue"]) == 1

    producers = client.get("/api/events/producers")
    assert producers.status_code == 200
    producer_names = {producer["subsystem"] for producer in producers.json()["producers"]}
    assert "tasks" in producer_names

    task_events = client.get(f"/api/events?surface=tasks&source_id={task_id}")
    assert task_events.status_code == 200
    event_text = str(task_events.json())
    assert "work-marker" not in event_text
    assert "raw task prompt" not in event_text
    assert "Task execution request was not executed." in event_text

    history_response = client.get("/api/workstation/history?limit=25")
    assert history_response.status_code == 200
    workstation_history = history_response.json()
    assert workstation_history["tasks"]["count"] == 2
    assert workstation_history["tasks"]["execution_enabled"] is False
    assert workstation_history["dashboard"]["tasks_count"] == 2
    assert "work-marker" not in str(workstation_history)
    assert "raw task prompt" not in str(workstation_history)

    second_client = TestClient(app)
    persisted = second_client.get(f"/api/tasks/{task_id}")
    assert persisted.status_code == 200
    assert persisted.json()["status"] == "done"
