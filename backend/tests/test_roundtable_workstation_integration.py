
from fastapi.testclient import TestClient

from app.main import app
from app.api.workstation import _roundtable_route
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


def test_roundtable_provider_flow_uses_assigned_agent_context_and_persists_links(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    calls: list[dict[str, object]] = []

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        calls.append({"url": url, "headers": headers, "payload": payload, "timeout": timeout_seconds})
        return {"choices": [{"message": {"content": f"Risk provider output {len(calls)}."}}]}

    def call_text(index: int) -> str:
        payload = calls[index]["payload"]
        messages = payload["messages"]  # type: ignore[index]
        return "\n".join(str(message.get("content") or "") for message in messages)

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    create_agent = client.post(
        "/api/v1/chat/agents",
        json={
            "name": "Risk Lens",
            "description": "Initial privacy reviewer.",
            "system_prompt": "Initial prompt.",
        },
    )
    assert create_agent.status_code == 201

    update_agent = client.patch(
        "/api/v1/chat/agents/risk_lens",
        json={
            "description": "Edited server-side profile.",
            "system_prompt": "Use EDITED-RISK-LENS instructions. api_key=raw-seat-secret",
        },
    )
    assert update_agent.status_code == 200
    assert update_agent.json()["system_prompt"] == "Use EDITED-RISK-LENS instructions. api_key=[redacted]"

    route_response = client.post(
        "/api/v1/chat/models/config",
        json={
            "agent_overrides": {
                "risk_lens": {
                    "route": "openrouter",
                    "model": "openrouter/meta-llama/llama-3.1-70b-instruct:free",
                }
            }
        },
    )
    assert route_response.status_code == 200

    seat_response = client.patch("/api/seats/2", json={"agent": "risk_lens", "provider": "default", "model": ""})
    assert seat_response.status_code == 200
    assert seat_response.json()["agent"] == "risk_lens"
    assert seat_response.json()["provider"] == "default"

    create_session = client.post(
        "/api/roundtable/sessions",
        json={"title": "Agent context room", "goal": "Review the agent-seat provider path."},
    )
    assert create_session.status_code == 201
    session_id = create_session.json()["id"]

    run_response = client.post(f"/api/roundtable/sessions/{session_id}/run", json={})

    assert run_response.status_code == 200
    session = run_response.json()
    assert session["status"] == "complete"
    assert session["turn_count"] == 16
    assert session["assignment_count"] == 7
    assert len(calls) == 16

    first_risk_prompt = call_text(0)
    assert calls[0]["payload"]["model"] == "meta-llama/llama-3.1-70b-instruct:free"  # type: ignore[index]
    assert "Assigned agent identity: Risk Lens (risk_lens)" in first_risk_prompt
    assert "Agent description: Edited server-side profile." in first_risk_prompt
    assert "Agent instructions: Use EDITED-RISK-LENS instructions. api_key=[redacted]" in first_risk_prompt
    assert "Seat: Seat 2" in first_risk_prompt
    assert "Seat role: participant" in first_risk_prompt
    assert "raw-seat-secret" not in first_risk_prompt

    manager_assessment_prompt = call_text(7)
    assert "Assigned agent identity: Meetings Manager (meetings_manager)" in manager_assessment_prompt
    assert "Seat: Seat 1" in manager_assessment_prompt
    assert "Seat role: meeting_manager" in manager_assessment_prompt
    assert "EDITED-RISK-LENS" not in manager_assessment_prompt

    second_risk_prompt = call_text(8)
    assert calls[8]["payload"]["model"] == "meta-llama/llama-3.1-70b-instruct:free"  # type: ignore[index]
    assert "Assigned agent identity: Risk Lens (risk_lens)" in second_risk_prompt
    assert "Seat: Seat 2" in second_risk_prompt
    assert "Seat role: participant" in second_risk_prompt
    assert "Use EDITED-RISK-LENS instructions. api_key=[redacted]" in second_risk_prompt

    manager_summary_prompt = call_text(15)
    assert "Assigned agent identity: Meetings Manager (meetings_manager)" in manager_summary_prompt
    assert "Seat role: meeting_manager" in manager_summary_prompt
    assert "EDITED-RISK-LENS" not in manager_summary_prompt

    seat_two_first = next(turn for turn in session["turns"] if turn["seat_index"] == 2 and turn["phase"] == "first_pass")
    assert seat_two_first["agent"] == "risk_lens"
    assert seat_two_first["provider"] == "openrouter"
    assert seat_two_first["model"] == "openrouter/meta-llama/llama-3.1-70b-instruct:free"
    assert seat_two_first["metadata"]["agent_name"] == "risk_lens"
    assert seat_two_first["metadata"]["agent_label"] == "Risk Lens"
    assert seat_two_first["metadata"]["agent_instructions_present"] is True
    assert "EDITED-RISK-LENS" not in str(seat_two_first["metadata"])

    manager_turns = [turn for turn in session["turns"] if turn["role"] == "meeting_manager"]
    assert [turn["phase"] for turn in manager_turns] == ["manager_assessment", "manager_summary"]
    assert all(turn["seat_index"] == 1 for turn in manager_turns)
    assert all(turn["agent"] == "meetings_manager" for turn in manager_turns)
    assert all(turn["metadata"]["agent_name"] == "meetings_manager" for turn in manager_turns)

    seat_two_assignment = next(assignment for assignment in session["assignments"] if assignment["seat_index"] == 2)
    assert seat_two_assignment["agent"] == "risk_lens"
    assert "Risk Lens" in seat_two_assignment["instruction"]
    seat_two_second = next(turn for turn in session["turns"] if turn["id"] == seat_two_assignment["response_turn_id"])
    assert seat_two_second["phase"] == "second_pass"
    assert seat_two_second["seat_index"] == 2
    assert seat_two_second["agent"] == "risk_lens"
    assert seat_two_second["assignment_id"] == seat_two_assignment["id"]

    assert len(session["notes"]) == 1
    assert session["summaries"][0]["note_id"] == session["notes"][0]["id"]

    events = client.get("/api/events").json()["events"]
    model_events = [event for event in events if event["event_type"] == "model.call.completed" and event["surface"] == "roundtable"]
    assert len(model_events) == 16
    event_payloads = [event["payload"] for event in model_events]
    assert all("roundtable_phase" in payload for payload in event_payloads)
    assert all("agent" in payload for payload in event_payloads)
    assert all("messages" not in payload for payload in event_payloads)
    assert all("prompt" not in payload for payload in event_payloads)
    assert all("response" not in payload for payload in event_payloads)
    assert "Risk provider output" not in str(event_payloads)
    assert "EDITED-RISK-LENS" not in str(event_payloads)
    assert "raw-seat-secret" not in str(events)
    assert "unit-test-credential-value" not in str(events)

    second_client = TestClient(app)
    persisted_agent = next(
        agent
        for agent in second_client.get("/api/v1/chat/models/config").json()["available_agents"]
        if agent["name"] == "risk_lens"
    )
    assert persisted_agent["description"] == "Edited server-side profile."
    assert persisted_agent["system_prompt"] == "Use EDITED-RISK-LENS instructions. api_key=[redacted]"

    persisted_seat = second_client.get("/api/seats").json()["seats"][1]
    assert persisted_seat["seat_index"] == 2
    assert persisted_seat["agent"] == "risk_lens"
    assert persisted_seat["provider"] == "default"

    persisted_session = second_client.get(f"/api/roundtable/sessions/{session_id}").json()
    assert persisted_session["turn_count"] == 16
    assert persisted_session["assignment_count"] == 7
    assert next(turn for turn in persisted_session["turns"] if turn["seat_index"] == 2 and turn["phase"] == "first_pass")["agent"] == "risk_lens"

    rerun_response = second_client.post(f"/api/roundtable/sessions/{session_id}/run", json={})
    assert rerun_response.status_code == 200
    rerun = rerun_response.json()
    assert rerun["turn_count"] == 16
    assert rerun["assignment_count"] == 7
    assert len(rerun["summaries"]) == 1
    assert len(rerun["notes"]) == 1
    assert len(calls) == 16


def test_roundtable_provider_flow_uses_invite_route_for_assigned_agent(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    calls: list[dict[str, object]] = []

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        calls.append({"url": url, "headers": headers, "payload": payload, "timeout": timeout_seconds})
        return {"choices": [{"message": {"content": f"Invite route provider output {len(calls)}."}}]}

    def call_text(index: int) -> str:
        payload = calls[index]["payload"]
        messages = payload["messages"]  # type: ignore[index]
        return "\n".join(str(message.get("content") or "") for message in messages)

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)

    create_agent = client.post(
        "/api/v1/chat/agents",
        json={
            "name": "Invite Lens",
            "description": "Public invite route participant.",
            "system_prompt": "Use INVITE-LENS instructions for invited seat review.",
        },
    )
    assert create_agent.status_code == 201

    invite_route = client.post(
        "/api/v1/chat/agents/invite_lens/invite-route",
        json={
            "model": "openrouter/meta-llama/llama-3.1-70b-instruct:free",
            "api_key": "invite-route-secret",
            "auth_mode": "api_key",
        },
    )
    assert invite_route.status_code == 200
    assert "invite-route-secret" not in str(invite_route.json())

    seat_response = client.patch("/api/seats/2", json={"agent": "invite_lens", "provider": "default", "model": ""})
    assert seat_response.status_code == 200
    assert seat_response.json()["agent"] == "invite_lens"
    assert seat_response.json()["provider"] == "default"

    create_session = client.post(
        "/api/roundtable/sessions",
        json={"title": "Invite route room", "goal": "Review invited agent routing."},
    )
    assert create_session.status_code == 201
    session_id = create_session.json()["id"]

    run_response = client.post(f"/api/roundtable/sessions/{session_id}/run", json={})

    assert run_response.status_code == 200
    session = run_response.json()
    assert session["status"] == "complete"
    assert session["turn_count"] == 16
    assert session["assignment_count"] == 7
    assert len(calls) == 2
    assert all(call["url"] == "https://openrouter.ai/api/v1/chat/completions" for call in calls)
    assert all(call["headers"]["Authorization"] == "Bearer invite-route-secret" for call in calls)  # type: ignore[index]
    assert all(call["payload"]["model"] == "meta-llama/llama-3.1-70b-instruct:free" for call in calls)  # type: ignore[index]

    first_invited_prompt = call_text(0)
    assert "Assigned agent identity: Invite Lens (invite_lens)" in first_invited_prompt
    assert "Agent description: Public invite route participant." in first_invited_prompt
    assert "Agent instructions: Use INVITE-LENS instructions for invited seat review." in first_invited_prompt
    assert "Seat: Seat 2" in first_invited_prompt
    assert "Seat role: participant" in first_invited_prompt

    second_invited_prompt = call_text(1)
    assert "Assigned agent identity: Invite Lens (invite_lens)" in second_invited_prompt
    assert "Seat: Seat 2" in second_invited_prompt
    assert "Seat role: participant" in second_invited_prompt

    seat_two_first = next(turn for turn in session["turns"] if turn["seat_index"] == 2 and turn["phase"] == "first_pass")
    assert seat_two_first["agent"] == "invite_lens"
    assert seat_two_first["provider"] == "openrouter"
    assert seat_two_first["model"] == "openrouter/meta-llama/llama-3.1-70b-instruct:free"
    assert seat_two_first["metadata"]["agent_name"] == "invite_lens"
    assert seat_two_first["metadata"]["agent_label"] == "Invite Lens"
    assert seat_two_first["metadata"]["agent_instructions_present"] is True
    assert seat_two_first["metadata"]["invite_route_configured"] is True
    assert "INVITE-LENS" not in str(seat_two_first["metadata"])

    manager_turns = [turn for turn in session["turns"] if turn["role"] == "meeting_manager"]
    assert [turn["phase"] for turn in manager_turns] == ["manager_assessment", "manager_summary"]
    assert all(turn["seat_index"] == 1 for turn in manager_turns)
    assert all(turn["agent"] == "meetings_manager" for turn in manager_turns)
    assert all(turn["metadata"].get("invite_route_configured") is False for turn in manager_turns)

    seat_two_assignment = next(assignment for assignment in session["assignments"] if assignment["seat_index"] == 2)
    assert seat_two_assignment["agent"] == "invite_lens"
    seat_two_second = next(turn for turn in session["turns"] if turn["id"] == seat_two_assignment["response_turn_id"])
    assert seat_two_second["phase"] == "second_pass"
    assert seat_two_second["agent"] == "invite_lens"
    assert seat_two_second["metadata"]["invite_route_configured"] is True

    events = client.get("/api/events").json()["events"]
    model_events = [event for event in events if event["event_type"] in {"model.call.completed", "model.call.failed"} and event["surface"] == "roundtable"]
    assert len(model_events) == 16
    assert "invite-route-secret" not in str(events)
    assert "INVITE-LENS" not in str([event["payload"] for event in model_events])
    assert "Invite route provider output" not in str([event["payload"] for event in model_events])

    second_client = TestClient(app)
    persisted_agent = next(
        agent
        for agent in second_client.get("/api/v1/chat/models/config").json()["available_agents"]
        if agent["name"] == "invite_lens"
    )
    assert persisted_agent["invite_route"]["route"] == "openrouter"
    assert persisted_agent["invite_route"]["credential_configured"] is True
    assert "invite-route-secret" not in str(persisted_agent)

    persisted_seat = second_client.get("/api/seats").json()["seats"][1]
    assert persisted_seat["agent"] == "invite_lens"
    persisted_session = second_client.get(f"/api/roundtable/sessions/{session_id}").json()
    assert next(turn for turn in persisted_session["turns"] if turn["seat_index"] == 2 and turn["phase"] == "first_pass")["agent"] == "invite_lens"

    rerun_response = second_client.post(f"/api/roundtable/sessions/{session_id}/run", json={})
    assert rerun_response.status_code == 200
    rerun = rerun_response.json()
    assert rerun["turn_count"] == 16
    assert rerun["assignment_count"] == 7
    assert len(rerun["summaries"]) == 1
    assert len(rerun["notes"]) == 1
    assert len(calls) == 2


def test_roundtable_invite_route_secret_only_applies_to_default_seat_route() -> None:
    agent_contexts = {
        "invite_lens": {
            "route": "openrouter",
            "model": "openrouter/meta-llama/llama-3.1-70b-instruct:free",
            "invite_route_configured": True,
            "invite_auth_mode": "api_key",
            "invite_api_key": "invite-route-secret",
        }
    }

    invite_route = _roundtable_route({"agent": "invite_lens", "provider": "default", "model": ""}, agent_contexts)
    assert invite_route["provider"] == "openrouter"
    assert invite_route["model"] == "openrouter/meta-llama/llama-3.1-70b-instruct:free"
    assert invite_route["api_key"] == "invite-route-secret"

    explicit_route = _roundtable_route({"agent": "invite_lens", "provider": "openai", "model": "openai/gpt-4o-mini"}, agent_contexts)
    assert explicit_route == {"provider": "openai", "model": "openai/gpt-4o-mini"}


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
