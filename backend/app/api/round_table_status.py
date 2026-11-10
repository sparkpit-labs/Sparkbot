from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

MeetingEngine = Literal["local-rooms"]
AgentOrchestration = Literal["runner-on-this-computer"]
ModelCalls = Literal["none-in-sparkbot"]
TurnPersistence = Literal["local-sqlite"]


class RoundTableSeat(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class RoundTableStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    meeting_engine: MeetingEngine
    agent_orchestration: AgentOrchestration
    model_calls: ModelCalls
    turn_persistence: TurnPersistence
    rooms_api: str
    seats: list[RoundTableSeat]


ROUND_TABLE_SEATS: list[RoundTableSeat] = [
    {
        "id": "owner",
        "label": "Owner",
        "status": "available",
        "notes": "You, in the Sparkbot app on this computer. Only owner messages wake agents.",
    },
    {
        "id": "agent",
        "label": "Agent seat",
        "status": "available",
        "notes": "An AI agent on this computer, joined with a seat key. It answers @mentions through a runner you start.",
    },
    {
        "id": "guest",
        "label": "Guest seat",
        "status": "planned",
        "notes": "People joining from other devices are planned. Rooms are local to this computer today.",
    },
]


@router.get("/round-table/status")
def round_table_status() -> RoundTableStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "available",
        "meeting_engine": "local-rooms",
        "agent_orchestration": "runner-on-this-computer",
        "model_calls": "none-in-sparkbot",
        "turn_persistence": "local-sqlite",
        "rooms_api": "/roundtable/rooms",
        "seats": ROUND_TABLE_SEATS,
    }


assert {seat["status"] for seat in ROUND_TABLE_SEATS} <= ALLOWED_CAPABILITY_STATUSES
