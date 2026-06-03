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


@router.get("/api/workstation/state")
async def workstation_state() -> dict[str, Any]:
    state = get_store().workstation_state()
    state["controls"] = await _build_controls_config()
    return state


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
async def delete_memory(memory_id: str, actor: str = "operator") -> dict[str, Any]:
    deleted = get_store().delete_memory(memory_id, actor=actor)
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


@router.post("/api/guardian/actions/confirmations", status_code=201)
async def create_confirmation(body: ConfirmationCreate) -> dict[str, Any]:
    return get_store().create_confirmation(body.model_dump(exclude={"actor"}), actor=body.actor)
