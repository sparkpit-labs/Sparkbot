from typing import Literal

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.services.local_workstation_store import (
    ALLOWED_CARD_STATUSES,
    ALLOWED_MESSAGE_ROLES,
    ALLOWED_WORK_LANES,
    LocalStoreError,
    LocalWorkstationStore,
    NotFoundError,
)

router = APIRouter(prefix="/local", tags=["local-workstation"])

MessageRole = Literal["operator", "note", "assistant-local"]
WorkLaneName = Literal["inbox", "planned", "active", "review", "done"]
WorkCardStatus = Literal["open", "in-progress", "blocked", "done"]


class ChatSessionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class ChatSessionUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class ChatMessageCreate(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1, max_length=8000)


class MemoryNoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=12000)
    source: str = Field(default="operator", min_length=1, max_length=80)


class MemoryNoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    body: str | None = Field(default=None, min_length=1, max_length=12000)
    source: str | None = Field(default=None, min_length=1, max_length=80)


class WorkLaneCardCreate(BaseModel):
    lane: WorkLaneName
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=12000)
    status: WorkCardStatus = "open"
    chat_session_id: str | None = Field(default=None, min_length=1, max_length=120)


class WorkLaneCardUpdate(BaseModel):
    lane: WorkLaneName | None = None
    title: str | None = Field(default=None, min_length=1, max_length=160)
    body: str | None = Field(default=None, min_length=1, max_length=12000)
    status: WorkCardStatus | None = None
    chat_session_id: str | None = Field(default=None, min_length=1, max_length=120)


def store() -> LocalWorkstationStore:
    return LocalWorkstationStore()


def handle_store_error(error: Exception) -> HTTPException:
    if isinstance(error, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, LocalStoreError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Local store error")


@router.get("/chat/sessions")
def list_chat_sessions() -> dict:
    return {"sessions": store().list_chat_sessions()}


@router.post("/chat/sessions", status_code=status.HTTP_201_CREATED)
def create_chat_session(payload: ChatSessionCreate) -> dict:
    try:
        return store().create_chat_session(payload.title)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.get("/chat/sessions/{session_id}")
def get_chat_session(session_id: str) -> dict:
    try:
        return store().get_chat_session(session_id)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.patch("/chat/sessions/{session_id}")
def update_chat_session(session_id: str, payload: ChatSessionUpdate) -> dict:
    try:
        return store().update_chat_session(session_id, payload.title)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.delete("/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(session_id: str) -> Response:
    try:
        store().delete_chat_session(session_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.post("/chat/sessions/{session_id}/messages", status_code=status.HTTP_201_CREATED)
def add_chat_message(session_id: str, payload: ChatMessageCreate) -> dict:
    if payload.role not in ALLOWED_MESSAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid local message role")
    try:
        return store().add_chat_message(session_id, payload.role, payload.content)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.get("/memory-notes")
def list_memory_notes() -> dict:
    return {"notes": store().list_memory_notes()}


@router.post("/memory-notes", status_code=status.HTTP_201_CREATED)
def create_memory_note(payload: MemoryNoteCreate) -> dict:
    try:
        return store().create_memory_note(payload.title, payload.body, payload.source)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.get("/memory-notes/{note_id}")
def get_memory_note(note_id: str) -> dict:
    try:
        return store().get_memory_note(note_id)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.patch("/memory-notes/{note_id}")
def update_memory_note(note_id: str, payload: MemoryNoteUpdate) -> dict:
    try:
        return store().update_memory_note(note_id, payload.title, payload.body, payload.source)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.delete("/memory-notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory_note(note_id: str) -> Response:
    try:
        store().delete_memory_note(note_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.get("/work-lane-cards")
def list_work_lane_cards() -> dict:
    return {"cards": store().list_work_lane_cards()}


@router.post("/work-lane-cards", status_code=status.HTTP_201_CREATED)
def create_work_lane_card(payload: WorkLaneCardCreate) -> dict:
    if payload.lane not in ALLOWED_WORK_LANES or payload.status not in ALLOWED_CARD_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid local work lane card value")
    try:
        return store().create_work_lane_card(payload.lane, payload.title, payload.body, payload.status, payload.chat_session_id)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.get("/work-lane-cards/{card_id}")
def get_work_lane_card(card_id: str) -> dict:
    try:
        return store().get_work_lane_card(card_id)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.patch("/work-lane-cards/{card_id}")
def update_work_lane_card(card_id: str, payload: WorkLaneCardUpdate) -> dict:
    try:
        chat_session_id = payload.chat_session_id if "chat_session_id" in payload.model_fields_set else None
        if "chat_session_id" in payload.model_fields_set:
            return store().update_work_lane_card(card_id, payload.lane, payload.title, payload.body, payload.status, chat_session_id)
        return store().update_work_lane_card(card_id, payload.lane, payload.title, payload.body, payload.status)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error


@router.delete("/work-lane-cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_lane_card(card_id: str) -> Response:
    try:
        store().delete_work_lane_card(card_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (LocalStoreError, NotFoundError) as error:
        raise handle_store_error(error) from error
