from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

ImplementationStatus = Literal["not-implemented"]


class ChatSurface(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class ChatStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    chat_runtime: ImplementationStatus
    message_persistence: ImplementationStatus
    model_calls: ImplementationStatus
    streaming: ImplementationStatus
    provider_routing: ImplementationStatus
    supported_surfaces: list[ChatSurface]


CHAT_SURFACES: list[ChatSurface] = [
    {
        "id": "chat-shell",
        "label": "Chat shell",
        "status": "preview",
        "notes": "Static chat shell preview. No messages are sent.",
    },
    {
        "id": "message-input",
        "label": "Message input",
        "status": "disabled-by-default",
        "notes": "Input remains disabled until chat runtime and safety gates exist.",
    },
    {
        "id": "model-response",
        "label": "Model response",
        "status": "guarded-future",
        "notes": "No model calls are implemented.",
    },
    {
        "id": "message-history",
        "label": "Message history",
        "status": "guarded-future",
        "notes": "No message persistence is implemented.",
    },
]


@router.get("/chat/status")
def chat_status() -> ChatStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "preview",
        "chat_runtime": "not-implemented",
        "message_persistence": "not-implemented",
        "model_calls": "not-implemented",
        "streaming": "not-implemented",
        "provider_routing": "not-implemented",
        "supported_surfaces": CHAT_SURFACES,
    }


assert {surface["status"] for surface in CHAT_SURFACES} <= ALLOWED_CAPABILITY_STATUSES
