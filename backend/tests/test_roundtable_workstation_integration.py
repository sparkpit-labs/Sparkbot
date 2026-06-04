
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


def test_roundtable_provider_safe_flow_persists_shared_state_events_and_wrapup_note(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
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

    session_id = created["id"]
    run_response = client.post(f"/api/roundtable/sessions/{session_id}/run", json={})
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
    assert phases == ["first_pass"] * 7 + ["manager_assessment"] + ["second_pass"] * 7 + ["manager_summary"]
    assert [turn["turn_index"] for turn in session["turns"]] == list(range(1, 17))
    manager_turns = [turn for turn in session["turns"] if turn["role"] == "meeting_manager"]
    assert [turn["phase"] for turn in manager_turns] == ["manager_assessment", "manager_summary"]
    assert all(turn["seat_index"] == 1 for turn in manager_turns)
    assert all(turn["provider"] == "provider-safe" for turn in session["turns"])
    assert all(assignment["status"] == "answered" for assignment in session["assignments"])
    assert all(assignment["response_turn_id"] for assignment in session["assignments"])
    second_pass_ids = {turn["id"] for turn in session["turns"] if turn["phase"] == "second_pass"}
    assert {assignment["response_turn_id"] for assignment in session["assignments"]} == second_pass_ids

    notes_response = client.get(f"/api/notes?surface=roundtable&source_id={session_id}")
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
    persisted = second_client.get(f"/api/roundtable/sessions/{session_id}")
    assert persisted.status_code == 200
    persisted_session = persisted.json()
    assert persisted_session["status"] == "complete"
    assert persisted_session["turn_count"] == 16
    assert persisted_session["assignment_count"] == 7
    assert len(persisted_session["summaries"]) == 1
    assert len(persisted_session["notes"]) == 1

    rerun_response = second_client.post(f"/api/roundtable/sessions/{session_id}/run", json={})
    assert rerun_response.status_code == 200
    rerun = rerun_response.json()
    assert rerun["turn_count"] == 16
    assert rerun["assignment_count"] == 7
    assert len(rerun["summaries"]) == 1
    assert len(rerun["notes"]) == 1


def test_roundtable_provider_model_flow_persists_provider_turns_and_redacted_events(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    calls: list[dict[str, object]] = []

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        calls.append({"url": url, "headers": headers, "payload": payload, "timeout": timeout_seconds})
        return {"choices": [{"message": {"content": f"Provider safe Round Table response {len(calls)}."}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    create_response = client.post(
        "/api/roundtable/sessions",
        json={"title": "Provider room", "goal": "Review a provider-backed Round Table plan."},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    run_response = client.post(f"/api/roundtable/sessions/{session_id}/run", json={})

    assert run_response.status_code == 200
    session = run_response.json()
    assert session["status"] == "complete"
    assert session["phase"] == "wrap_up"
    assert session["turn_count"] == 16
    assert session["assignment_count"] == 7
    assert len(calls) == 16
    assert all(call["url"] == "https://openrouter.ai/api/v1/chat/completions" for call in calls)
    assert all(call["payload"]["model"] == "openai/gpt-4o-mini" for call in calls)

    assert all(turn["provider"] == "openrouter" for turn in session["turns"])
    assert all(turn["model"] == "openrouter/openai/gpt-4o-mini" for turn in session["turns"])
    assert all(turn["metadata"]["mode"] == "provider_backed" for turn in session["turns"])
    assert all(turn["metadata"]["model_execution_status"] == "success" for turn in session["turns"])
    assert all(turn["metadata"]["model_event_id"] for turn in session["turns"])
    assert session["summaries"][0]["content"] == "Provider safe Round Table response 16."

    events = client.get("/api/events?event_type=model.call.completed").json()["events"]
    model_events = [event for event in events if event["surface"] == "roundtable" and event["source_id"] == session_id]
    assert len(model_events) == 16
    assert all(event["payload"]["status"] == "success" for event in model_events)
    assert all("roundtable_phase" in event["payload"] for event in model_events)
    assert "Provider safe Round Table response" not in str([event["payload"] for event in model_events])
    assert "unit-test-credential-value" not in str(events)


def test_roundtable_model_output_blocked_before_persisting_turns(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        return {"choices": [{"message": {"content": "I will send email after this room."}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    create_response = client.post(
        "/api/roundtable/sessions",
        json={"title": "Protected output room", "goal": "Review the plan safely."},
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

    events = client.get("/api/events").json()["events"]
    blocked_events = [event for event in events if event["event_type"] == "guardian.action_blocked" and event["surface"] == "roundtable"]
    assert blocked_events
    assert blocked_events[0]["payload"]["action_type"] == "external_send"
    assert blocked_events[0]["payload"]["source"] == "model_output"
    assert blocked_events[0]["payload"]["model_event_id"]
    assert "I will send email" not in str(events)


def test_roundtable_privileged_request_fails_closed_and_logs_guardian_block(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
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


def test_roundtable_blocks_privileged_categories_without_turn_or_note_mutation(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    cases = [
        ("external_send", "Publish the manager summary to a channel."),
        ("connector_action", "Run connector sync after the room closes."),
        ("file_mutation", "Write file output for the room."),
        ("process_action", "Start process for the room output."),
        ("scheduler_action", "Schedule job for later follow-up."),
        ("device_action", "Control device from this meeting."),
    ]

    for expected_action, goal in cases:
        create_response = client.post(
            "/api/roundtable/sessions",
            json={"title": f"Blocked {expected_action}", "goal": goal},
        )
        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        run_response = client.post(f"/api/roundtable/sessions/{session_id}/run", json={})
        assert run_response.status_code == 200
        session = run_response.json()
        assert session["status"] == "blocked"
        assert session["phase"] == "guardian_blocked"
        assert session["blocked_action"] == expected_action
        assert session["turns"] == []
        assert session["assignments"] == []
        assert session["summaries"] == []
        assert session["notes"] == []

    state = client.get("/api/workstation/state").json()
    assert state["roundtable"]["sessions_count"] == len(cases)
    assert state["roundtable"]["turns_count"] == 0
    assert state["roundtable"]["assignments_count"] == 0
    assert state["roundtable"]["summaries_count"] == 0
    assert state["dashboard"]["notes_count"] == 0

    events = client.get("/api/events").json()["events"]
    blocked_actions = {
        event["payload"]["action_type"]
        for event in events
        if event["event_type"] == "guardian.action_blocked" and event["surface"] == "roundtable"
    }
    assert blocked_actions == {action for action, _goal in cases}
