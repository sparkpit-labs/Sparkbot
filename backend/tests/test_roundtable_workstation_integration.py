
from fastapi.testclient import TestClient

from app.main import app


def test_roundtable_provider_safe_flow_persists_shared_state_events_and_wrapup_note(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    memory_response = client.post(
        "/api/memory",
        json={
            "content": "Provider-safe meetings should use shared context before making a plan.",
            "memory_type": "preference",
            "source_surface": "workstation",
            "tags": ["roundtable"],
        },
    )
    assert memory_response.status_code == 201
    note_response = client.post(
        "/api/notes",
        json={
            "title": "Planning note",
            "body": "Save meeting notes at manager wrap-up only.",
            "surface": "workstation",
            "tags": ["roundtable"],
        },
    )
    assert note_response.status_code == 201

    create_response = client.post(
        "/api/roundtable/sessions",
        json={
            "title": "Launch planning room",
            "goal": "Plan a provider-safe Round Table launch review.",
            "metadata": {"api_key": "example-value", "nested": {"token": "example-token"}},
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "setup"
    assert created["phase"] == "intake"
    assert created["metadata"]["api_key"] == "[redacted]"
    assert created["participants"][0]["role"] == "meeting_manager"

    run_response = client.post(f"/api/roundtable/sessions/{created["id"]}/run", json={})
    assert run_response.status_code == 200
    session = run_response.json()
    assert session["status"] == "complete"
    assert session["phase"] == "wrap_up"
    assert session["room"]["phase"] == "roundtable_complete"
    assert session["turn_count"] == 16
    assert session["assignment_count"] == 7
    assert len(session["summaries"]) == 1
    assert len(session["notes"]) == 1
    assert session["summaries"][0]["note_id"] == session["notes"][0]["id"]

    phases = [turn["phase"] for turn in session["turns"]]
    assert phases.count("first_pass") == 7
    assert phases.count("manager_assessment") == 1
    assert phases.count("second_pass") == 7
    assert phases.count("manager_summary") == 1
    assert all(turn["provider"] == "provider-safe" for turn in session["turns"])
    assert all(assignment["status"] == "answered" for assignment in session["assignments"])
    assert all(assignment["response_turn_id"] for assignment in session["assignments"])

    notes_response = client.get(f"/api/notes?surface=roundtable&source_id={created["id"]}")
    assert notes_response.status_code == 200
    assert notes_response.json()["count"] == 1

    state = client.get("/api/workstation/state").json()
    assert state["roundtable"]["sessions_count"] == 1
    assert state["roundtable"]["turns_count"] == 16
    assert state["roundtable"]["assignments_count"] == 7
    assert state["roundtable"]["summaries_count"] == 1
    assert state["dashboard"]["roundtable_sessions_count"] == 1
    assert state["dashboard"]["roundtable_turns_count"] == 16

    events = client.get("/api/events").json()["events"]
    event_types = {event["event_type"] for event in events}
    assert "roundtable.session.created" in event_types
    assert "roundtable.context.recalled" in event_types
    assert "roundtable.turn.created" in event_types
    assert "roundtable.assignment.created" in event_types
    assert "roundtable.summary.created" in event_types
    assert "note.saved" in event_types
    created_event = next(event for event in events if event["event_type"] == "roundtable.session.created")
    assert created_event["payload"]["metadata"]["api_key"] == "[redacted]"
    assert created_event["payload"]["metadata"]["nested"]["token"] == "[redacted]"

    second_client = TestClient(app)
    persisted = second_client.get(f"/api/roundtable/sessions/{created["id"]}")
    assert persisted.status_code == 200
    persisted_session = persisted.json()
    assert persisted_session["status"] == "complete"
    assert persisted_session["turn_count"] == 16
    assert persisted_session["assignment_count"] == 7
    assert len(persisted_session["summaries"]) == 1
    assert len(persisted_session["notes"]) == 1


def test_roundtable_privileged_request_fails_closed_and_logs_guardian_block(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/roundtable/sessions",
        json={"title": "Blocked request", "goal": "Send email and run command after the meeting."},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    run_response = client.post(f"/api/roundtable/sessions/{session_id}/run", json={})
    assert run_response.status_code == 200
    blocked = run_response.json()
    assert blocked["status"] == "blocked"
    assert blocked["phase"] == "guardian_blocked"
    assert blocked["blocked_action"] == "external_send"
    assert blocked["turns"] == []
    assert blocked["assignments"] == []
    assert blocked["summaries"] == []
    assert blocked["notes"] == []

    state = client.get("/api/workstation/state").json()
    assert state["roundtable"]["sessions_count"] == 1
    assert state["roundtable"]["turns_count"] == 0
    assert state["roundtable"]["assignments_count"] == 0
    assert state["roundtable"]["summaries_count"] == 0

    events = client.get("/api/events").json()["events"]
    blocked_events = [event for event in events if event["event_type"] == "guardian.action_blocked" and event["surface"] == "roundtable"]
    assert blocked_events
    assert blocked_events[0]["payload"]["requires_confirmation"] is True
    assert blocked_events[0]["payload"]["action_type"] == "external_send"
