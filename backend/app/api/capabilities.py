from typing import Literal, TypedDict

from fastapi import APIRouter

router = APIRouter()

CapabilityStatus = Literal["available", "preview", "planned"]


class Capability(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class CapabilitiesResponse(TypedDict):
    service: str
    mode: str
    capabilities: list[Capability]


CAPABILITIES: list[Capability] = [
    {
        "id": "backend-health",
        "label": "Backend health endpoint",
        "status": "available",
        "notes": "Read-only local health check.",
    },
    {
        "id": "frontend-shell",
        "label": "Frontend shell",
        "status": "available",
        "notes": "Public shell interface.",
    },
    {
        "id": "workstation",
        "label": "Workstation shell",
        "status": "available",
        "notes": "Navigation and product shell preview.",
    },
    {
        "id": "chat",
        "label": "Chat shell",
        "status": "preview",
        "notes": "No model calls or message persistence.",
    },
    {
        "id": "round-table",
        "label": "Round Table",
        "status": "preview",
        "notes": "No meeting engine or agent orchestration.",
    },
    {
        "id": "provider-setup",
        "label": "Provider Setup",
        "status": "preview",
        "notes": "No credential storage or provider calls.",
    },
    {
        "id": "guardian-controls",
        "label": "Guardian Controls",
        "status": "preview",
        "notes": "No policy enforcement runtime.",
    },
    {
        "id": "desktop-packaging",
        "label": "Desktop packaging",
        "status": "planned",
        "notes": "No installer or desktop binary yet.",
    },
]


@router.get("/capabilities")
def capabilities() -> CapabilitiesResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "capabilities": CAPABILITIES,
    }
