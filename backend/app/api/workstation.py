from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.command_center import DEFAULT_AGENTS, _build_controls_config, _custom_agent_records, _invite_route_records, _read_config, _read_secrets
from app.services.model_execution import ModelExecutionResult, execute_model_request, resolve_model_route
from app.services.workstation_store import _redact_sensitive_text, get_store


router = APIRouter()


class SeatUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=80)
    agent: str | None = Field(default=None, max_length=80)
    provider: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=200)
    actor: str = Field(default="operator", max_length=80)


class RoomCreate(BaseModel):
    title: str = Field(default="Workstation Room", max_length=160)
    status: str = Field(default="open", max_length=40)
    phase: str = Field(default="setup", max_length=80)
    goal: str = Field(default="", max_length=2000)
    summary: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    actor: str = Field(default="operator", max_length=80)


class RoomUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=160)
    status: str | None = Field(default=None, max_length=40)
    phase: str | None = Field(default=None, max_length=80)
    goal: str | None = Field(default=None, max_length=2000)
    summary: str | None = Field(default=None, max_length=4000)
    metadata: dict[str, Any] | None = None
    actor: str = Field(default="operator", max_length=80)


class NoteCreate(BaseModel):
    title: str = Field(default="Workstation note", max_length=200)
    body: str = Field(min_length=1, max_length=20000)
    surface: str = Field(default="workstation", max_length=80)
    source_id: str = Field(default="", max_length=160)
    actor: str = Field(default="operator", max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=20)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    body: str | None = Field(default=None, max_length=20000)
    surface: str | None = Field(default=None, max_length=80)
    source_id: str | None = Field(default=None, max_length=160)
    actor: str = Field(default="operator", max_length=80)
    tags: list[str] | None = Field(default=None, max_length=20)


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=20000)
    memory_type: str = Field(default="note", max_length=80)
    source_surface: str = Field(default="workstation", max_length=80)
    source_id: str = Field(default="", max_length=160)
    actor: str = Field(default="operator", max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=20)


class MemoryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=20000)
    memory_type: str | None = Field(default=None, max_length=80)
    source_surface: str | None = Field(default=None, max_length=80)
    source_id: str | None = Field(default=None, max_length=160)
    actor: str = Field(default="operator", max_length=80)
    tags: list[str] | None = Field(default=None, max_length=20)


class MemoryRecallRequest(BaseModel):
    query: str = Field(default="", max_length=2000)
    tags: list[str] = Field(default_factory=list, max_length=20)
    limit: int = Field(default=8, ge=1, le=50)


class EventCreate(BaseModel):
    event_type: str = Field(default="workstation.event", max_length=120)
    surface: str = Field(default="workstation", max_length=80)
    source_id: str = Field(default="", max_length=160)
    actor: str = Field(default="operator", max_length=80)
    summary: str = Field(default="Workstation event.", max_length=400)
    payload: dict[str, Any] = Field(default_factory=dict)


class ConfirmationCreate(BaseModel):
    action_type: str = Field(default="workstation.action", max_length=120)
    risk_level: str = Field(default="confirm", max_length=80)
    prompt: str = Field(default="Confirm this action before continuing.", max_length=800)
    surface: str = Field(default="workstation", max_length=80)
    source_id: str = Field(default="", max_length=160)
    actor: str = Field(default="operator", max_length=80)


class ConfirmationDecision(BaseModel):
    decision: str = Field(pattern="^(approved|denied)$")
    actor: str = Field(default="operator", max_length=80)


class TaskCreate(BaseModel):
    title: str = Field(default="Workstation task", min_length=1, max_length=200)
    notes: str = Field(default="", max_length=12000)
    status: str = Field(default="open", max_length=40)
    surface: str = Field(default="workstation", max_length=80)
    source_id: str = Field(default="", max_length=160)
    actor: str = Field(default="operator", max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=20)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = Field(default=None, max_length=12000)
    status: str | None = Field(default=None, max_length=40)
    surface: str | None = Field(default=None, max_length=80)
    source_id: str | None = Field(default=None, max_length=160)
    actor: str = Field(default="operator", max_length=80)
    tags: list[str] | None = Field(default=None, max_length=20)
    metadata: dict[str, Any] | None = None


class TaskOperationRequest(BaseModel):
    actor: str = Field(default="operator", max_length=80)


class ChatSessionCreate(BaseModel):
    title: str = Field(default="Sparkbot chat", max_length=160)
    active_room_id: str = Field(default="", max_length=160)
    metadata: dict[str, Any] = Field(default_factory=dict)
    actor: str = Field(default="operator", max_length=80)


class ChatMessageCreate(BaseModel):
    session_id: str | None = Field(default=None, max_length=160)
    content: str = Field(min_length=1, max_length=20000)
    actor: str = Field(default="operator", max_length=80)
    save_to_memory: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class RoundTableSessionCreate(BaseModel):
    room_id: str = Field(default="", max_length=160)
    title: str = Field(default="Round Table Room", max_length=160)
    goal: str = Field(default="", max_length=4000)
    context_query: str = Field(default="", max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    actor: str = Field(default="operator", max_length=80)


class RoundTableRunRequest(BaseModel):
    actor: str = Field(default="operator", max_length=80)


async def _workstation_state_with_controls() -> dict[str, Any]:
    state = get_store().workstation_state()
    state["controls"] = await _build_controls_config()
    return state


def _selected_chat_route(state: dict[str, Any]) -> dict[str, Any]:
    controls = state.get("controls") if isinstance(state.get("controls"), dict) else {}
    default = controls.get("default_selection") if isinstance(controls.get("default_selection"), dict) else {}
    seats = state.get("seats") if isinstance(state.get("seats"), list) else []
    seat_one = seats[0] if seats else {}
    model = str(default.get("model") or seat_one.get("model") or "local-workstation")
    provider = str(default.get("provider") or seat_one.get("provider") or "local")
    if provider == "default":
        provider = "local"
    return {
        "provider": provider or "local",
        "model": model or "local-workstation",
        "label": str(default.get("label") or model or "Local Workstation"),
        "seat_index": seat_one.get("seat_index") or 1,
        "seat_label": seat_one.get("label") or "Seat 1",
        "agent": seat_one.get("agent") or "meetings_manager",
    }


def _chat_notes_for_context(store: Any, session_id: str) -> list[dict[str, Any]]:
    notes = store.list_notes(limit=100)
    scoped_notes: list[dict[str, Any]] = []
    for note in notes:
        surface = note.get("surface")
        source_id = note.get("source_id")
        if surface == "chat" and source_id == session_id:
            scoped_notes.append(note)
        elif surface in {"workstation", "memory", "room"} and len(scoped_notes) < 8:
            scoped_notes.append(note)
    return scoped_notes[:8]


def _memory_delete_target(content: str, memories: list[dict[str, Any]]) -> str | None:
    normalized = content.lower()
    if "memory" not in normalized:
        return None
    if not any(term in normalized for term in ("delete", "remove", "forget", "erase")):
        return None
    for memory in memories:
        memory_id = str(memory.get("id") or "")
        if memory_id and memory_id.lower() in normalized:
            return memory_id
    return None


def _command_center_guardrails_text() -> str:
    config = _read_config()
    if not bool(config.get("security_guardrails_enabled")):
        return ""
    custom_guardrails = _redact_sensitive_text(str(config.get("custom_guardrails") or "").strip())
    if not custom_guardrails:
        return ""
    return f"\n\nOperator-provided Command Center guardrails:\n{custom_guardrails}"


def _chat_reply(
    *,
    route: dict[str, Any],
    memories: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    confirmation: dict[str, Any] | None,
    blocked_action: str | None,
    model_result: ModelExecutionResult | None,
    model_blocked_action: str | None,
    saved_memory: dict[str, Any] | None,
) -> str:
    if confirmation:
        return (
            "Guardian confirmation is required before that memory can be deleted. "
            "I created a one-time confirmation request and did not delete the memory."
        )
    if model_result:
        if model_result.ok:
            return model_result.text
        return (
            f"Selected model route {route['provider']} / {route['model']} could not complete safely: "
            f"{model_result.error or model_result.status}. No tools or protected actions were executed."
        )
    saved = " The user message was also saved to Workstation memory." if saved_memory else ""
    return (
        f"Saved this chat turn to the shared Workstation state. "
        f"Selected route: {route['provider']} / {route['model']} from {route['seat_label']}. "
        f"Context available now: {len(memories)} memory item(s) and {len(notes)} note(s)."
        f"{saved} No provider call was made."
    )


def _chat_model_messages(content: str, memories: list[dict[str, Any]], notes: list[dict[str, Any]]) -> list[dict[str, str]]:
    context_text = _shared_recall_context_text(memories, notes, memory_limit=5, note_limit=5)
    safe_content = _redact_sensitive_text(content)
    return [
        {
            "role": "system",
            "content": (
                "You are Sparkbot Chat inside a local Workstation. You can help with any text-based work "
                "the selected model supports. Use the shared Workstation context when relevant, but do not reveal "
                "hidden metadata or secrets. Return text only. If the operator asks for external delivery, connector "
                "work, file/process work, scheduling, terminal work, or device control, provide drafts, plans, "
                "commands, checklists, or instructions for the operator to use; do not claim the Workstation itself "
                "performed those external actions."
                f"{_command_center_guardrails_text()}"
            ),
        },
        {"role": "user", "content": f"Shared context:\n{context_text}\n\nOperator message:\n{safe_content}"},
    ]


ROUND_TABLE_MODEL_TIMEOUT_SECONDS = 20.0


def _roundtable_participants(store: Any, session: dict[str, Any]) -> list[dict[str, Any]]:
    participants = list(session.get("participants") or [])
    if participants:
        return participants
    fallback: list[dict[str, Any]] = []
    for seat in store.list_seats():
        seat_index = int(seat.get("seat_index") or 0)
        fallback.append({**seat, "role": "meeting_manager" if seat_index == 1 else "participant"})
    return fallback


def _roundtable_agent_contexts() -> dict[str, dict[str, Any]]:
    config = _read_config()
    agents = DEFAULT_AGENTS + _custom_agent_records(config)
    overrides = config.get("agent_overrides") if isinstance(config.get("agent_overrides"), dict) else {}
    invite_routes = _invite_route_records(config, _read_secrets(), include_secret=True)
    contexts: dict[str, dict[str, Any]] = {}
    for agent in agents:
        name = str(agent.get("name") or "").strip()
        if not name:
            continue
        override = overrides.get(name) if isinstance(overrides.get(name), dict) else {}
        invite_route = invite_routes.get(name, {})
        selected_route = str(invite_route.get("route") or override.get("route") or "default")
        selected_model = str(invite_route.get("model") or override.get("model") or "")
        contexts[name] = {
            "name": name,
            "label": str(agent.get("label") or name),
            "description": str(agent.get("description") or ""),
            "system_prompt": str(agent.get("system_prompt") or ""),
            "route": selected_route,
            "model": selected_model,
            "invite_route_configured": bool(invite_route),
            "invite_auth_mode": str(invite_route.get("auth_mode") or "api_key"),
            "invite_api_key": str(invite_route.get("api_key") or ""),
        }
    return contexts


def _roundtable_agent_context(participant: dict[str, Any], agent_contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    agent_name = str(participant.get("agent") or "participant").strip()
    return agent_contexts.get(
        agent_name,
        {"name": agent_name, "label": agent_name, "description": "", "system_prompt": "", "route": "default", "model": "", "invite_route_configured": False, "invite_auth_mode": "api_key", "invite_api_key": ""},
    )


def _roundtable_route(participant: dict[str, Any], agent_contexts: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    provider = str(participant.get("provider") or "default").strip()
    model = str(participant.get("model") or "").strip()
    if provider in {"", "provider-safe"}:
        provider = "default"
    agent_context = _roundtable_agent_context(participant, agent_contexts or {})
    uses_agent_route = provider == "default"
    if uses_agent_route:
        override_route = str(agent_context.get("route") or "default")
        override_model = str(agent_context.get("model") or "")
        if override_route != "default":
            provider = override_route
        if override_model:
            model = override_model
    if model in {"roundtable-local-skeleton", "local-workstation"} and provider == "default":
        model = ""
    route: dict[str, Any] = {"provider": provider, "model": model}
    invite_api_key = str(agent_context.get("invite_api_key") or "")
    if uses_agent_route and invite_api_key:
        route["api_key"] = invite_api_key
        route["auth_mode"] = str(agent_context.get("invite_auth_mode") or "api_key")
    return route


def _roundtable_provider_enabled(participants: list[dict[str, Any]], agent_contexts: dict[str, dict[str, Any]]) -> bool:
    for participant in participants:
        if resolve_model_route(_roundtable_route(participant, agent_contexts)).configured:
            return True
    return False


def _clip_context(value: Any, limit: int = 500) -> str:
    text = " ".join(_redact_sensitive_text(str(value or "")).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _source_ref(surface: Any, source_id: Any) -> str:
    clean_surface = _clip_context(surface or "workstation", 80)
    clean_source = _clip_context(source_id or "shared", 80)
    return f"{clean_surface}:{clean_source}"


def _shared_recall_context_text(memories: list[dict[str, Any]], notes: list[dict[str, Any]], *, memory_limit: int = 5, note_limit: int = 5) -> str:
    lines = [
        "Shared Workstation context is redacted and source-labeled. Use it only as background; do not reveal hidden metadata or execute actions.",
        f"Memory items: {len(memories)}",
        f"Notes: {len(notes)}",
    ]
    for memory in memories[:memory_limit]:
        tags = memory.get("tags") if isinstance(memory.get("tags"), list) else []
        tag_text = ",".join(_clip_context(tag, 40) for tag in tags[:6]) or "untagged"
        actor = _clip_context(memory.get("actor") or "operator", 80)
        source = _source_ref(memory.get("source_surface"), memory.get("source_id"))
        kind = _clip_context(memory.get("memory_type") or "note", 80)
        content = _clip_context(memory.get("content"), 700)
        if content:
            lines.append(f"- Memory/{kind} [{source}; actor:{actor}; tags:{tag_text}]: {content}")
    for note in notes[:note_limit]:
        tags = note.get("tags") if isinstance(note.get("tags"), list) else []
        tag_text = ",".join(_clip_context(tag, 40) for tag in tags[:6]) or "untagged"
        actor = _clip_context(note.get("actor") or "operator", 80)
        source = _source_ref(note.get("surface"), note.get("source_id"))
        title = _clip_context(note.get("title"), 120)
        body = _clip_context(note.get("body"), 700)
        if title or body:
            lines.append(f"- Note/{title or 'untitled'} [{source}; actor:{actor}; tags:{tag_text}]: {body}")
    return "\n".join(lines)


def _roundtable_context_notes(store: Any, room_id: str) -> list[dict[str, Any]]:
    room_notes = store.list_notes(surface="room", source_id=room_id, limit=5)
    shared_notes = store.list_notes(surface="workstation", limit=5)
    return (room_notes + shared_notes)[:8]


def _roundtable_context_text(memories: list[dict[str, Any]], notes: list[dict[str, Any]]) -> str:
    return _shared_recall_context_text(memories, notes, memory_limit=5, note_limit=5)


def _roundtable_model_messages(
    *,
    session: dict[str, Any],
    participant: dict[str, Any],
    agent_context: dict[str, Any],
    phase: str,
    role: str,
    instruction: str,
    context_text: str,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are one Sparkbot Round Table seat in a local-first public Workstation. "
                f"Assigned agent identity: {agent_context.get('label') or agent_context.get('name') or 'Participant'} "
                f"({agent_context.get('name') or 'participant'}). "
                f"Agent description: {agent_context.get('description') or 'No additional description.'} "
                f"Agent instructions: {agent_context.get('system_prompt') or 'Use the assigned role and meeting phase.'} "
                "Return concise text only. You can help with any text-based work the selected model supports. "
                "If the meeting asks for external delivery, connector work, file/process work, scheduling, "
                "terminal work, or device control, provide drafts, plans, commands, checklists, or instructions "
                "for the operator to use; do not claim the Workstation itself performed those external actions."
                f"{_command_center_guardrails_text()}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Round Table title: {session.get('title') or 'Round Table Room'}\n"
                f"Goal: {session.get('goal') or session.get('title') or 'Review the room goal.'}\n"
                f"Phase: {phase}\n"
                f"Seat: {participant.get('label') or 'Seat'}\n"
                f"Seat role: {role}\n"
                f"Assigned agent: {agent_context.get('label') or participant.get('agent') or 'participant'} "
                f"({agent_context.get('name') or participant.get('agent') or 'participant'})\n\n"
                f"Shared context:\n{context_text}\n\n"
                f"Instruction:\n{instruction}\n\n"
                "Return 2 to 4 sentences."
            ),
        },
    ]


def _provider_turn_metadata(result: ModelExecutionResult, mode: str, agent_context: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "mode": mode,
        "model_execution_status": result.status,
        "model_event_id": result.event_id,
        "duration_ms": result.duration_ms,
        "agent_name": agent_context.get("name") or "participant",
        "agent_label": agent_context.get("label") or agent_context.get("name") or "Participant",
        "agent_instructions_present": bool(agent_context.get("system_prompt")),
        "invite_route_configured": bool(agent_context.get("invite_route_configured")),
    }
    if result.error:
        metadata["model_execution_error"] = result.error
    return metadata


async def _roundtable_model_turn(
    *,
    store: Any,
    session: dict[str, Any],
    participant: dict[str, Any],
    phase: str,
    role: str,
    instruction: str,
    context_text: str,
    fallback_content: str,
    agent_contexts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    agent_context = _roundtable_agent_context(participant, agent_contexts)
    result = await execute_model_request(
        route=_roundtable_route(participant, agent_contexts),
        messages=_roundtable_model_messages(
            session=session,
            participant=participant,
            agent_context=agent_context,
            phase=phase,
            role=role,
            instruction=instruction,
            context_text=context_text,
        ),
        store=store,
        surface="roundtable",
        source_id=str(session["id"]),
        actor="sparkbot",
        timeout_seconds=ROUND_TABLE_MODEL_TIMEOUT_SECONDS,
        event_metadata={
            "mode": "roundtable",
            "roundtable_phase": phase,
            "roundtable_role": role,
            "seat_index": participant.get("seat_index"),
            "agent": agent_context.get("name") or participant.get("agent") or "participant",
            "agent_label": agent_context.get("label") or agent_context.get("name") or "Participant",
            "invite_route_configured": bool(agent_context.get("invite_route_configured")),
        },
    )
    if result.ok:
        safe_text = _redact_sensitive_text(result.text)
        return {
            "participant": participant,
            "content": safe_text,
            "provider": result.provider,
            "model": result.model,
            "metadata": _provider_turn_metadata(result, "provider_backed", agent_context),
        }
    return {
        "participant": participant,
        "content": fallback_content,
        "provider": "provider-safe",
        "model": "roundtable-local-skeleton",
        "metadata": _provider_turn_metadata(result, "provider_safe_fallback", agent_context),
    }


async def _build_roundtable_model_run(
    *,
    store: Any,
    session: dict[str, Any],
    participants: list[dict[str, Any]],
) -> dict[str, Any]:
    session_id = str(session["id"])
    room_id = str(session["room_id"])
    title = str(session.get("title") or "Round Table Room")
    goal = str(session.get("goal") or title)
    context_query = str(session.get("context_query") or goal)
    memories = store.recall_memory(query=context_query, limit=5)
    context_notes = _roundtable_context_notes(store, room_id)
    context_text = _roundtable_context_text(memories, context_notes)
    agent_contexts = _roundtable_agent_contexts()

    manager = next((item for item in participants if item.get("seat_index") == 1), participants[0])
    workers = [item for item in participants if item.get("seat_index") != manager.get("seat_index")]
    if not workers:
        workers = participants

    first_turns: list[dict[str, Any]] = []
    for worker in workers:
        fallback = (
            f"{worker.get('label') or 'Seat'} ({_roundtable_agent_context(worker, agent_contexts).get('label') or worker.get('agent') or 'participant'}) first pass: for '{goal}', "
            f"keep the response text-only, identify useful assumptions, and contribute from the assigned agent role. "
            f"Shared context available: {len(memories)} memory item(s), "
            f"{len(context_notes)} note(s)."
        )
        turn = await _roundtable_model_turn(
            store=store,
            session=session,
            participant=worker,
            phase="first_pass",
            role="participant",
            instruction=(
                f"Give a first-pass contribution for '{goal}' from the assigned {_roundtable_agent_context(worker, agent_contexts).get('label') or worker.get('agent') or 'participant'} agent role. "
                "Produce text work only; do not claim the app executed external steps."
            ),
            context_text=context_text,
            fallback_content=fallback,
            agent_contexts=agent_contexts,
        )
        if turn.get("blocked_action"):
            return turn
        first_turns.append(turn)

    first_pass_brief = "\n".join(f"- {item['participant'].get('label') or 'Seat'}: {_clip_context(item.get('content'), 500)}" for item in first_turns)
    manager_fallback = (
        f"Seat 1 Meeting Manager assessment: the room has enough first-pass input to split '{goal}' into focused assignments. "
        "No external actions were executed by the app."
    )
    manager_assessment = await _roundtable_model_turn(
        store=store,
        session=session,
        participant=manager,
        phase="manager_assessment",
        role="meeting_manager",
        instruction=f"Assess the first-pass contributions and identify the assignment strategy.\n{first_pass_brief}",
        context_text=context_text,
        fallback_content=manager_fallback,
        agent_contexts=agent_contexts,
    )
    if manager_assessment.get("blocked_action"):
        return manager_assessment

    assignments: list[dict[str, Any]] = []
    for worker in workers:
        instruction = (
            f"Review '{goal}' from the {_roundtable_agent_context(worker, agent_contexts).get('label') or worker.get('agent') or 'participant'} perspective. Return a concise second-pass "
            "recommendation, risks, and the next operator step. Produce text only; do not claim the app executed external steps."
        )
        assignments.append(
            {
                "id": str(uuid.uuid4()),
                "worker": worker,
                "title": f"Assignment for {worker.get('label') or 'Seat'}",
                "instruction": instruction,
            }
        )

    second_turns: list[dict[str, Any]] = []
    for assignment in assignments:
        worker = dict(assignment["worker"])
        fallback = (
            f"{worker.get('label') or 'Seat'} ({_roundtable_agent_context(worker, agent_contexts).get('label') or worker.get('agent') or 'participant'}) second pass: complete assignment "
            f"'{assignment['instruction']}'. Recommendation for '{goal}': keep scope narrow, make the result usable for operator review, "
            "and record the decision in shared state."
        )
        turn = await _roundtable_model_turn(
            store=store,
            session=session,
            participant=worker,
            phase="second_pass",
            role="participant",
            instruction=str(assignment["instruction"]),
            context_text=context_text,
            fallback_content=fallback,
            agent_contexts=agent_contexts,
        )
        if turn.get("blocked_action"):
            return turn
        turn["assignment_id"] = assignment["id"]
        second_turns.append(turn)

    second_pass_brief = "\n".join(f"- {item['participant'].get('label') or 'Seat'}: {_clip_context(item.get('content'), 500)}" for item in second_turns)
    summary_fallback = (
        f"Meeting Manager wrap-up for '{goal}': first-pass ideas were collected, assignments were answered, "
        f"and the next operator step is to review the plan before any external execution outside this text-only meeting. Context used: {len(memories)} "
        f"memory item(s) and {len(context_notes)} note(s)."
    )
    manager_summary = await _roundtable_model_turn(
        store=store,
        session=session,
        participant=manager,
        phase="manager_summary",
        role="meeting_manager",
        instruction=f"Create the manager wrap-up and next-step plan from the second-pass responses.\n{second_pass_brief}",
        context_text=context_text,
        fallback_content=summary_fallback,
        agent_contexts=agent_contexts,
    )
    if manager_summary.get("blocked_action"):
        return manager_summary

    return {
        "room_id": room_id,
        "title": title,
        "memory_count": len(memories),
        "note_count": len(context_notes),
        "first_turns": first_turns,
        "manager_assessment": manager_assessment,
        "assignments": assignments,
        "second_turns": second_turns,
        "manager_summary": manager_summary,
    }


@router.get("/api/workstation/state")
async def workstation_state() -> dict[str, Any]:
    return await _workstation_state_with_controls()


@router.get("/api/workstation/history")
async def workstation_history(limit: int = Query(default=25, ge=1, le=100)) -> dict[str, Any]:
    history = get_store().workstation_history(limit=limit)
    history["controls"] = await _build_controls_config()
    return history


@router.get("/api/chat/sessions")
async def list_chat_sessions(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    sessions = get_store().list_chat_sessions(limit=limit)
    return {"sessions": sessions, "count": len(sessions)}


@router.post("/api/chat/sessions", status_code=201)
async def create_chat_session(body: ChatSessionCreate) -> dict[str, Any]:
    return get_store().create_chat_session(body.model_dump(exclude={"actor"}), actor=body.actor)


@router.get("/api/chat/sessions/{session_id}")
async def get_chat_session(session_id: str) -> dict[str, Any]:
    session = get_store().get_chat_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    return session


@router.post("/api/chat/messages", status_code=201)
async def add_chat_turn(body: ChatMessageCreate) -> dict[str, Any]:
    store = get_store()
    state = await _workstation_state_with_controls()
    route = _selected_chat_route(state)
    resolved_route = resolve_model_route(route)
    route = {**route, "provider": resolved_route.provider, "model": resolved_route.model, "label": resolved_route.label}

    safe_content = _redact_sensitive_text(body.content)

    if body.session_id:
        session = store.get_chat_session(body.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        title = safe_content.strip()[:80] or "Sparkbot chat"
        session = store.create_chat_session({"title": title, "metadata": {"surface": "chat"}}, actor=body.actor)

    session_id = str(session["id"])
    try:
        user_message = store.add_chat_message(
            session_id,
            {
                "role": "user",
                "content": safe_content,
                "provider": route["provider"],
                "model": route["model"],
                "metadata": {"source": "chat", **body.metadata},
            },
            actor=body.actor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    memories = store.recall_memory(query=safe_content, limit=5)
    notes = _chat_notes_for_context(store, session_id)
    store.append_event(
        {
            "event_type": "chat.context.recalled",
            "surface": "chat",
            "source_id": session_id,
            "summary": "Chat recalled shared Workstation context.",
            "payload": {"memory_count": len(memories), "note_count": len(notes), "message_id": user_message["id"] if user_message else ""},
        },
        actor=body.actor,
    )

    saved_memory = None
    if body.save_to_memory:
        try:
            saved_memory = store.create_memory(
                {
                    "content": safe_content,
                    "memory_type": "chat",
                    "source_surface": "chat",
                    "source_id": session_id,
                    "tags": ["chat"],
                },
                actor=body.actor,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    delete_target = _memory_delete_target(safe_content, store.list_memory(limit=500))
    confirmation = None
    blocked_action = None
    if delete_target:
        confirmation = store.create_confirmation(
            {
                "action_type": "memory.delete",
                "risk_level": "confirm",
                "prompt": "Confirm memory delete before the chat can continue with that action.",
                "surface": "memory",
                "source_id": delete_target,
            },
            actor=body.actor,
        )

    model_result = None
    model_blocked_action = None
    if not confirmation:
        model_result = await execute_model_request(
            route=route,
            messages=_chat_model_messages(safe_content, memories, notes),
            store=store,
            surface="chat",
            source_id=session_id,
            actor="sparkbot",
        )

    assistant_text = _chat_reply(
        route=route,
        memories=memories,
        notes=notes,
        confirmation=confirmation,
        blocked_action=blocked_action,
        model_result=model_result,
        model_blocked_action=model_blocked_action,
        saved_memory=saved_memory,
    )
    assistant_message = store.add_chat_message(
        session_id,
        {
            "role": "assistant",
            "content": assistant_text,
            "provider": route["provider"],
            "model": route["model"],
            "metadata": {
                "mode": "provider_execution" if model_result and model_result.ok else "provider_not_called" if not model_result else "provider_failed_safe",
                "model_execution_status": model_result.status if model_result else "not_called",
                "model_event_id": model_result.event_id if model_result else "",
                "confirmation_id": confirmation["id"] if confirmation else "",
                "blocked_action": blocked_action or model_blocked_action or "",
            },
        },
        actor="sparkbot",
    )

    return {
        "session": store.get_chat_session(session_id),
        "user_message": user_message,
        "assistant_message": assistant_message,
        "route": route,
        "context": {"memories": memories, "notes": notes},
        "saved_memory": saved_memory,
        "guardian_confirmation": confirmation,
        "blocked_action": blocked_action or model_blocked_action,
        "model_execution": {
            "status": model_result.status if model_result else "not_called",
            "provider": route["provider"],
            "model": route["model"],
            "event_id": model_result.event_id if model_result else "",
            "error": model_result.error if model_result else "",
        },
        "workstation": await _workstation_state_with_controls(),
    }


@router.get("/api/roundtable/sessions")
async def list_roundtable_sessions(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    sessions = get_store().list_roundtable_sessions(limit=limit)
    return {"sessions": sessions, "count": len(sessions)}


@router.post("/api/roundtable/sessions", status_code=201)
async def create_roundtable_session(body: RoundTableSessionCreate) -> dict[str, Any]:
    try:
        return get_store().create_roundtable_session(body.model_dump(exclude={"actor"}), actor=body.actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/roundtable/sessions/{session_id}")
async def get_roundtable_session(session_id: str) -> dict[str, Any]:
    session = get_store().get_roundtable_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Round Table session not found.")
    return session


@router.post("/api/roundtable/sessions/{session_id}/run")
async def run_roundtable_session(session_id: str, body: RoundTableRunRequest | None = None) -> dict[str, Any]:
    actor = body.actor if body else "operator"
    store = get_store()
    session = store.get_roundtable_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Round Table session not found.")
    if session["status"] in {"complete", "blocked"} or session["turns"] or session["assignments"] or session["summaries"]:
        return session

    room_id = str(session["room_id"])

    participants = _roundtable_participants(store, session)
    agent_contexts = _roundtable_agent_contexts()
    if not _roundtable_provider_enabled(participants, agent_contexts):
        fallback_session = store.run_roundtable_session(session_id, actor=actor)
        if not fallback_session:
            raise HTTPException(status_code=404, detail="Round Table session not found.")
        return fallback_session

    run = await _build_roundtable_model_run(store=store, session=session, participants=participants)
    if run.get("blocked_action"):
        blocked = store.block_roundtable_session(
            session_id,
            room_id,
            str(run["blocked_action"]),
            actor="sparkbot",
            source="model_output",
            model_event_id=str(run.get("model_event_id") or ""),
        )
        if not blocked:
            raise HTTPException(status_code=404, detail="Round Table session not found.")
        return blocked

    persisted = store.persist_roundtable_model_session(session_id, actor=actor, run=run)
    if not persisted:
        raise HTTPException(status_code=404, detail="Round Table session not found.")
    return persisted


@router.get("/api/seats")
async def list_seats() -> dict[str, Any]:
    seats = get_store().list_seats()
    return {"seats": seats, "count": len(seats)}


@router.patch("/api/seats/{seat_index}")
async def update_seat(seat_index: int, body: SeatUpdate) -> dict[str, Any]:
    try:
        return get_store().update_seat(
            seat_index,
            {key: value for key, value in body.model_dump(exclude={"actor"}).items() if value is not None},
            actor=body.actor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/seats/{seat_index}")
async def update_seat_post(seat_index: int, body: SeatUpdate) -> dict[str, Any]:
    return await update_seat(seat_index, body)


@router.get("/api/rooms")
async def list_rooms(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    rooms = get_store().list_rooms(limit=limit)
    return {"rooms": rooms, "count": len(rooms)}


@router.post("/api/rooms", status_code=201)
async def create_room(body: RoomCreate) -> dict[str, Any]:
    return get_store().create_room(body.model_dump(exclude={"actor"}), actor=body.actor)


@router.get("/api/rooms/{room_id}")
async def get_room(room_id: str) -> dict[str, Any]:
    room = get_store().get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    return room


@router.patch("/api/rooms/{room_id}")
async def update_room(room_id: str, body: RoomUpdate) -> dict[str, Any]:
    room = get_store().update_room(
        room_id,
        {key: value for key, value in body.model_dump(exclude={"actor"}).items() if value is not None},
        actor=body.actor,
    )
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    return room


@router.get("/api/notes")
async def list_notes(
    surface: str | None = None,
    source_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    notes = get_store().list_notes(surface=surface, source_id=source_id, limit=limit)
    return {"notes": notes, "count": len(notes)}


@router.post("/api/notes", status_code=201)
async def create_note(body: NoteCreate) -> dict[str, Any]:
    return get_store().create_note(body.model_dump(exclude={"actor"}), actor=body.actor)


@router.get("/api/notes/{note_id}")
async def get_note(note_id: str) -> dict[str, Any]:
    note = get_store().get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


@router.patch("/api/notes/{note_id}")
async def update_note(note_id: str, body: NoteUpdate) -> dict[str, Any]:
    note = get_store().update_note(
        note_id,
        {key: value for key, value in body.model_dump(exclude={"actor"}).items() if value is not None},
        actor=body.actor,
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


@router.get("/api/tasks")
async def list_tasks(
    limit: int = Query(default=50, ge=1, le=200),
    status: str | None = None,
) -> dict[str, Any]:
    try:
        tasks = get_store().list_tasks(limit=limit, status=status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"tasks": tasks, "count": len(tasks), "execution_enabled": False}


@router.post("/api/tasks", status_code=201)
async def create_task(body: TaskCreate) -> dict[str, Any]:
    try:
        return get_store().create_task(body.model_dump(exclude={"actor"}), actor=body.actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/tasks/{task_id}")
async def get_task(task_id: str) -> dict[str, Any]:
    task = get_store().get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@router.patch("/api/tasks/{task_id}")
async def update_task(task_id: str, body: TaskUpdate) -> dict[str, Any]:
    try:
        task = get_store().update_task(task_id, {key: value for key, value in body.model_dump(exclude={"actor"}).items() if value is not None}, actor=body.actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@router.get("/api/tasks/{task_id}/history")
async def get_task_history(task_id: str, limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
    if not get_store().get_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found.")
    history = get_store().list_task_history(task_id=task_id, limit=limit)
    return {"history": history, "count": len(history)}


async def _task_state_operation(task_id: str, operation: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    actor = body.actor if body else "operator"
    try:
        task = get_store().transition_task(task_id, operation, actor=actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@router.post("/api/tasks/{task_id}/pause")
async def pause_task(task_id: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    return await _task_state_operation(task_id, "pause", body)


@router.post("/api/tasks/{task_id}/resume")
async def resume_task(task_id: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    return await _task_state_operation(task_id, "resume", body)


@router.post("/api/tasks/{task_id}/done")
async def complete_task(task_id: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    return await _task_state_operation(task_id, "done", body)


@router.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    return await _task_state_operation(task_id, "cancel", body)


async def _blocked_task_execution(task_id: str, operation: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    actor = body.actor if body else "operator"
    task = get_store().block_task_execution(task_id, operation, actor=actor)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    raise HTTPException(status_code=403, detail="Task execution is disabled in the public Workstation boundary.")


@router.post("/api/tasks/{task_id}/run")
async def run_task(task_id: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    return await _blocked_task_execution(task_id, "run", body)


@router.post("/api/tasks/{task_id}/write-mode")
async def task_write_mode(task_id: str, body: TaskOperationRequest | None = None) -> dict[str, Any]:
    return await _blocked_task_execution(task_id, "write_mode", body)


@router.get("/api/memory")
async def list_memory(
    limit: int = Query(default=100, ge=1, le=500),
    tag: str | None = None,
    memory_type: str | None = None,
) -> dict[str, Any]:
    memories = get_store().list_memory(limit=limit, tag=tag, memory_type=memory_type)
    return {"memories": memories, "count": len(memories)}


@router.post("/api/memory", status_code=201)
async def create_memory(body: MemoryCreate) -> dict[str, Any]:
    try:
        return get_store().create_memory(body.model_dump(exclude={"actor"}), actor=body.actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/api/memory/{memory_id}")
async def update_memory(memory_id: str, body: MemoryUpdate) -> dict[str, Any]:
    try:
        memory = get_store().update_memory(
            memory_id,
            {key: value for key, value in body.model_dump(exclude={"actor"}).items() if value is not None},
            actor=body.actor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return memory


@router.post("/api/memory/recall")
async def recall_memory(body: MemoryRecallRequest) -> dict[str, Any]:
    memories = get_store().recall_memory(query=body.query, limit=body.limit, tags=body.tags)
    return {"memories": memories, "count": len(memories)}


@router.delete("/api/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    confirmation_id: str | None = None,
    actor: str = "operator",
) -> dict[str, Any]:
    store = get_store()
    authorized, detail = store.authorize_action(
        confirmation_id=confirmation_id,
        action_type="memory.delete",
        surface="memory",
        source_id=memory_id,
        actor=actor,
    )
    if not authorized:
        raise HTTPException(status_code=403, detail=detail)
    deleted = store.delete_memory(memory_id, actor=actor)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return {"deleted": memory_id}


@router.get("/api/events/producers")
async def list_event_producers() -> dict[str, Any]:
    producers = get_store().event_producers()
    return {"producers": producers, "count": len(producers)}


@router.get("/api/events")
async def list_events(
    limit: int = Query(default=100, ge=1, le=500),
    event_type: str | None = None,
    surface: str | None = None,
    source_id: str | None = None,
) -> dict[str, Any]:
    events = get_store().list_events(limit=limit, event_type=event_type, surface=surface, source_id=source_id)
    return {"events": events, "count": len(events)}


@router.post("/api/events", status_code=201)
async def append_event(body: EventCreate) -> dict[str, Any]:
    return get_store().append_event(body.model_dump(exclude={"actor"}), actor=body.actor)


@router.get("/api/guardian/actions/confirmations")
async def list_confirmations(
    limit: int = Query(default=50, ge=1, le=200),
    status: str | None = None,
) -> dict[str, Any]:
    confirmations = get_store().list_confirmations(limit=limit, status=status)
    return {"confirmations": confirmations, "count": len(confirmations)}


@router.post("/api/guardian/actions/confirmations", status_code=201)
async def create_confirmation(body: ConfirmationCreate) -> dict[str, Any]:
    return get_store().create_confirmation(body.model_dump(exclude={"actor"}), actor=body.actor)


@router.post("/api/guardian/actions/confirmations/{confirmation_id}/decision")
async def decide_confirmation(confirmation_id: str, body: ConfirmationDecision) -> dict[str, Any]:
    try:
        confirmation = get_store().decide_confirmation(confirmation_id, body.decision, actor=body.actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not confirmation:
        raise HTTPException(status_code=404, detail="Confirmation not found.")
    return confirmation
