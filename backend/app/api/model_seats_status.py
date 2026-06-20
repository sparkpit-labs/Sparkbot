from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

ImplementationStatus = Literal["not-implemented"]


class ModelSeat(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class ModelSeatsStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    model_calls: ImplementationStatus
    model_routing: ImplementationStatus
    provider_credentials: ImplementationStatus
    seat_persistence: ImplementationStatus
    seats: list[ModelSeat]


MODEL_SEATS: list[ModelSeat] = [
    {
        "id": "default-assistant",
        "label": "Default Assistant Seat",
        "status": "preview",
        "notes": "Read-only seat preview. No model is assigned or called.",
    },
    {
        "id": "research-seat",
        "label": "Research Seat",
        "status": "planned",
        "notes": "Future seat for research workflows. No runtime behavior is implemented.",
    },
    {
        "id": "builder-seat",
        "label": "Builder Seat",
        "status": "planned",
        "notes": "Future seat for implementation workflows. No tool execution is implemented.",
    },
    {
        "id": "reviewer-seat",
        "label": "Reviewer Seat",
        "status": "planned",
        "notes": "Future seat for review workflows. No model routing is implemented.",
    },
]


@router.get("/model-seats/status")
def model_seats_status() -> ModelSeatsStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "preview",
        "model_calls": "not-implemented",
        "model_routing": "not-implemented",
        "provider_credentials": "not-implemented",
        "seat_persistence": "not-implemented",
        "seats": MODEL_SEATS,
    }


assert {seat["status"] for seat in MODEL_SEATS} <= ALLOWED_CAPABILITY_STATUSES
