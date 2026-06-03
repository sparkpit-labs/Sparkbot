from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.command_center import _build_controls_config
from app.services.workstation_store import get_store


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


async def _workstation_state_with_controls() -> dict[str, Any]:
    state = get_store().workstation_state()
    state["controls"] = await _build_controls_config()
    return state


def _selected_chat_route(state: dict[str, Any]) -> dict[str, Any]:
    controls = state.get("controls") if isinstance(state.get("controls"), dict) else {}
    default = controls.get("default_selection") if isinstance(controls.get("default_selection"), dict) else {}
    seats = state.get("seats") if isinstance(state.get("seats"), list) else []
    seat_one = seats[0] if seats else {}
    model = str(seat_one.get("model") or default.get("model") or "local-workstation")
    provider = str(seat_one.get("provider") or default.get("provider") or "local")
    if provider == "default" and default.get("provider"):
        provider = str(default.get("provider"))
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


def _unsupported_privileged_request(content: str) -> str | None:
    normalized = content.lower()
    checks = (
        ("external_send", ("send email", "post message", "publish", "webhook")),
        ("connector_action", ("run connector", "sync calendar", "push to repo")),
        ("file_mutation", ("delete file", "write file", "modify file")),
        ("process_action", ("run command", "execute command", "start process")),
        ("room_execution", ("run room", "start meeting engine", "execute room")),
    )
    for action_type, terms in checks:
        if any(term in normalized for term in terms):
            return action_type
    return None


def _chat_reply(
    *,
    route: dict[str, Any],
    memories: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    confirmation: dict[str, Any] | None,
    blocked_action: str | None,
    saved_memory: dict[str, Any] | None,
) -> str:
    if confirmation:
        return (
            "Guardian confirmation is required before that memory can be deleted. "
            "I created a one-time confirmation request and did not delete the memory."
        )
    if blocked_action:
        return (
            "That request is treated as privileged Workstation work. "
            "No action was executed; a dedicated route and Guardian confirmation are required first."
        )
    saved = " The user message was also saved to Workstation memory." if saved_memory else ""
    return (
        f"Saved this chat turn to the shared Workstation state. "
        f"Selected route: {route['provider']} / {route['model']} from {route['seat_label']}. "
        f"Context available now: {len(memories)} memory item(s) and {len(notes)} note(s)."
        f"{saved} Provider execution remains deferred in this branch."
    )


@router.get("/api/workstation/state")
async def workstation_state() -> dict[str, Any]:
    return await _workstation_state_with_controls()


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

    if body.session_id:
        session = store.get_chat_session(body.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        title = body.content.strip()[:80] or "Sparkbot chat"
        session = store.create_chat_session({"title": title, "metadata": {"surface": "chat"}}, actor=body.actor)

    session_id = str(session["id"])
    try:
        user_message = store.add_chat_message(
            session_id,
            {
                "role": "user",
                "content": body.content,
                "provider": route["provider"],
                "model": route["model"],
                "metadata": {"source": "chat", **body.metadata},
            },
            actor=body.actor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    memories = store.recall_memory(query=body.content, limit=5)
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
                    "content": body.content,
                    "memory_type": "chat",
                    "source_surface": "chat",
                    "source_id": session_id,
                    "tags": ["chat"],
                },
                actor=body.actor,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    delete_target = _memory_delete_target(body.content, store.list_memory(limit=500))
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
    else:
        blocked_action = _unsupported_privileged_request(body.content)
        if blocked_action:
            store.append_event(
                {
                    "event_type": "guardian.action_blocked",
                    "surface": "chat",
                    "source_id": session_id,
                    "summary": "Privileged chat request was not executed.",
                    "payload": {"action_type": blocked_action, "requires_confirmation": True},
                },
                actor=body.actor,
            )

    assistant_text = _chat_reply(
        route=route,
        memories=memories,
        notes=notes,
        confirmation=confirmation,
        blocked_action=blocked_action,
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
                "mode": "provider_deferred",
                "confirmation_id": confirmation["id"] if confirmation else "",
                "blocked_action": blocked_action or "",
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
        "blocked_action": blocked_action,
        "workstation": await _workstation_state_with_controls(),
    }


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


@router.get("/api/events")
async def list_events(limit: int = Query(default=100, ge=1, le=500), event_type: str | None = None) -> dict[str, Any]:
    events = get_store().list_events(limit=limit, event_type=event_type)
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
