"""Roundtable API: local rooms where the owner and AI agent seats talk.

Two kinds of callers:

* The owner, using the Sparkbot app on this computer. Owner routes need the
  ``X-Sparkbot-Local: 1`` header (a browser only sends it from an allowed
  origin, after a CORS check) and a loopback ``Host``.
* Agent seats, using a seat key (``Authorization: Bearer rts_...``). A seat can
  only read and post in its own room and pick up its own @mention jobs.

Sparkbot makes no model calls here. Agents run on the owner's computer through
``sparkbot-roundtable.py run``, which the owner starts and stops.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.local_access import require_local_host
from app.services.roundtable_store import (
    JobConflict,
    RoundtableError,
    RoundtableNotFound,
    RoundtableStore,
)

router = APIRouter(prefix="/roundtable", tags=["roundtable"])

LONG_POLL_MAX_SECONDS = 30
LONG_POLL_STEP_SECONDS = 1.0


def store() -> RoundtableStore:
    return RoundtableStore()


def require_owner(
    request: Request,
    x_sparkbot_local: str | None = Header(default=None, alias="x-sparkbot-local"),
) -> None:
    require_local_host(request)
    if x_sparkbot_local != "1":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Owner requests must come from the Sparkbot app on this computer")


def require_seat(request: Request, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    require_local_host(request)
    scheme, _, key = (authorization or "").partition(" ")
    seat = store().authenticate_seat(key.strip()) if scheme.lower() == "bearer" else None
    if seat is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or removed seat key")
    return seat


def _fail(error: Exception) -> HTTPException:
    if isinstance(error, RoundtableNotFound):
        return HTTPException(status.HTTP_404_NOT_FOUND, str(error))
    return HTTPException(status.HTTP_400_BAD_REQUEST, str(error))


def _conflict(error: JobConflict) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(error), "status": error.job_status})


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class SeatCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=60)
    slug: str = Field(min_length=2, max_length=31)


class OwnerMessage(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    sender_name: str = Field(default="Owner", min_length=1, max_length=60)


class SeatMessage(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    reply_to_id: str | None = Field(default=None, max_length=64)


class PauseBody(BaseModel):
    paused: bool


class ClaimBody(BaseModel):
    claim_token: str = Field(min_length=1, max_length=200)


class HeartbeatBody(ClaimBody):
    note: str | None = Field(default=None, max_length=120)


class CompleteBody(ClaimBody):
    content: str = Field(min_length=1, max_length=8000)


class FailBody(ClaimBody):
    error: str = Field(default="failed", max_length=200)
    retry: bool = False


# -- owner ------------------------------------------------------------------

owner = APIRouter(dependencies=[Depends(require_owner)])


@owner.get("/rooms")
def list_rooms() -> dict:
    return {"rooms": store().list_rooms()}


@owner.post("/rooms", status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate) -> dict:
    try:
        return store().create_room(payload.name)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@owner.get("/rooms/{room_id}")
def get_room(room_id: str) -> dict:
    try:
        rt = store()
        return {**rt.get_room(room_id), "seats": rt.list_seats(room_id)}
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@owner.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: str) -> Response:
    try:
        store().delete_room(room_id)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@owner.get("/rooms/{room_id}/messages")
def list_messages(room_id: str, after: int = Query(default=0, ge=0), limit: int = Query(default=200, ge=1, le=500)) -> dict:
    try:
        return {"messages": store().list_messages(room_id, after, limit)}
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@owner.post("/rooms/{room_id}/messages", status_code=status.HTTP_201_CREATED)
def post_message(room_id: str, payload: OwnerMessage) -> dict:
    try:
        return store().post_owner_message(room_id, payload.content, payload.sender_name)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@owner.post("/rooms/{room_id}/pause")
def pause_room(room_id: str, payload: PauseBody) -> dict:
    try:
        return store().set_paused(room_id, payload.paused)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@owner.get("/rooms/{room_id}/seats")
def list_seats(room_id: str) -> dict:
    try:
        return {"seats": store().list_seats(room_id)}
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@owner.post("/rooms/{room_id}/seats", status_code=status.HTTP_201_CREATED)
def create_seat(room_id: str, payload: SeatCreate) -> dict:
    try:
        return store().create_seat(room_id, payload.display_name, payload.slug)
    except RoundtableError as error:
        if "already in this room" in str(error):
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
        raise _fail(error) from error
    except RoundtableNotFound as error:
        raise _fail(error) from error


@owner.post("/rooms/{room_id}/seats/{seat_id}/rotate")
def rotate_seat(room_id: str, seat_id: str) -> dict:
    try:
        return store().rotate_seat_key(room_id, seat_id)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@owner.delete("/rooms/{room_id}/seats/{seat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_seat(room_id: str, seat_id: str) -> Response:
    try:
        store().delete_seat(room_id, seat_id)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -- seats ------------------------------------------------------------------

seat_router = APIRouter(prefix="/seat")


@seat_router.get("/me")
def seat_me(seat: dict = Depends(require_seat)) -> dict:
    return {
        "seat": {"id": seat["id"], "slug": seat["slug"], "display_name": seat["display_name"], "kind": "agent"},
        "rooms": [{"id": seat["room_id"], "name": seat["room_name"], "role": "agent"}],
    }


@seat_router.get("/messages")
def seat_messages(
    after: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    seat: dict = Depends(require_seat),
) -> dict:
    return {"messages": store().list_messages(seat["room_id"], after, limit)}


@seat_router.post("/messages", status_code=status.HTTP_201_CREATED)
def seat_post(payload: SeatMessage, seat: dict = Depends(require_seat)) -> dict:
    try:
        return store().post_seat_message(seat, payload.content, payload.reply_to_id)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@seat_router.get("/jobs/next", response_model=None)
def next_job(request: Request, wait: int = Query(default=0, ge=0, le=LONG_POLL_MAX_SECONDS), seat: dict = Depends(require_seat)) -> Any:
    rt = store()
    deadline = time.monotonic() + wait
    shutdown = getattr(request.app.state, "desktop_shutdown", None)
    while True:
        if shutdown is not None and shutdown.is_set():
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        job = rt.claim_next(seat)
        if job is not None:
            return {"job": job}
        if time.monotonic() >= deadline:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        if shutdown is not None:
            shutdown.wait(LONG_POLL_STEP_SECONDS)
        else:
            time.sleep(LONG_POLL_STEP_SECONDS)


@seat_router.post("/jobs/{job_id}/heartbeat", response_model=None)
def job_heartbeat(job_id: str, payload: HeartbeatBody, seat: dict = Depends(require_seat)) -> Any:
    try:
        return {"job": store().heartbeat(seat, job_id, payload.claim_token, payload.note)}
    except JobConflict as error:
        return _conflict(error)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@seat_router.post("/jobs/{job_id}/complete", response_model=None)
def job_complete(job_id: str, payload: CompleteBody, seat: dict = Depends(require_seat)) -> Any:
    try:
        return store().complete(seat, job_id, payload.claim_token, payload.content)
    except JobConflict as error:
        return _conflict(error)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


@seat_router.post("/jobs/{job_id}/fail", response_model=None)
def job_fail(job_id: str, payload: FailBody, seat: dict = Depends(require_seat)) -> Any:
    try:
        return {"job": store().fail(seat, job_id, payload.claim_token, payload.error, payload.retry)}
    except JobConflict as error:
        return _conflict(error)
    except (RoundtableError, RoundtableNotFound) as error:
        raise _fail(error) from error


router.include_router(owner)
router.include_router(seat_router)
