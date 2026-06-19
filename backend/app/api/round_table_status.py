from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

ImplementationStatus = Literal["not-implemented"]


class RoundTableSeat(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class RoundTableStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    meeting_engine: ImplementationStatus
    agent_orchestration: ImplementationStatus
    model_calls: ImplementationStatus
    turn_persistence: ImplementationStatus
    seats: list[RoundTableSeat]


ROUND_TABLE_SEATS: list[RoundTableSeat] = [
    {
        "id": "operator",
        "label": "Operator",
        "status": "preview",
        "notes": "Human operator role shown as part of the shell preview.",
    },
    {
        "id": "assistant",
        "label": "Assistant seat",
        "status": "preview",
        "notes": "Assistant role preview only. No model calls are made.",
    },
    {
        "id": "research",
        "label": "Research seat",
        "status": "planned",
        "notes": "Research role is planned. No agent runtime is implemented.",
    },
    {
        "id": "builder",
        "label": "Builder seat",
        "status": "planned",
        "notes": "Builder role is planned. No tool execution is implemented.",
    },
    {
        "id": "reviewer",
        "label": "Reviewer seat",
        "status": "planned",
        "notes": "Reviewer role is planned. No review workflow runtime is implemented.",
    },
]


@router.get("/round-table/status")
def round_table_status() -> RoundTableStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "preview",
        "meeting_engine": "not-implemented",
        "agent_orchestration": "not-implemented",
        "model_calls": "not-implemented",
        "turn_persistence": "not-implemented",
        "seats": ROUND_TABLE_SEATS,
    }


assert {seat["status"] for seat in ROUND_TABLE_SEATS} <= ALLOWED_CAPABILITY_STATUSES
