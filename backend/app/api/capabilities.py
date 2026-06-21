from typing import Literal, TypedDict

from fastapi import APIRouter

router = APIRouter()

CapabilityStatus = Literal["available", "preview", "planned", "disabled-by-default", "guarded-future"]
ALLOWED_CAPABILITY_STATUSES: set[str] = {
    "available",
    "preview",
    "planned",
    "disabled-by-default",
    "guarded-future",
}


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
        "id": "local-workstation-store",
        "label": "Local Workstation store",
        "status": "available",
        "notes": "Local SQLite storage for Workstation data.",
    },
    {
        "id": "local-chat-drafts",
        "label": "Local chat drafts",
        "status": "available",
        "notes": "Stores operator and note messages locally without model calls.",
    },
    {
        "id": "local-memory-notes",
        "label": "Local memory notes",
        "status": "available",
        "notes": "Stores local notes and supports explicit per-prompt selection without automatic retrieval or model memory.",
    },
    {
        "id": "local-work-lane-cards",
        "label": "Local work lane cards",
        "status": "available",
        "notes": "Stores local planning cards and optional local chat-session links without scheduler or task execution.",
    },
    {
        "id": "local-data-export",
        "label": "Local data export",
        "status": "available",
        "notes": "Downloads a read-only JSON backup of local Workstation data without import, sync, or upload.",
    },
    {
        "id": "local-runtime-settings",
        "label": "Local runtime settings",
        "status": "available",
        "notes": "Shows env-driven local runtime paths and Ollama settings without credential fields or save actions.",
    },
    {
        "id": "local-model-adapter",
        "label": "Local model adapter",
        "status": "disabled-by-default",
        "notes": "Localhost-only Ollama adapter; prompt calls require explicit operator enablement.",
    },
    {
        "id": "local-ollama",
        "label": "Local Ollama",
        "status": "disabled-by-default",
        "notes": "Uses only localhost or 127.0.0.1 and no credentials or cloud providers.",
    },
    {
        "id": "workstation",
        "label": "Workstation shell",
        "status": "preview",
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
        "label": "Provider Setup shell",
        "status": "preview",
        "notes": "No credential storage or provider calls.",
    },
    {
        "id": "model-seats",
        "label": "Model Seat preview",
        "status": "preview",
        "notes": "No model assignment, routing, calls, credentials, or seat persistence.",
    },
    {
        "id": "work-lanes",
        "label": "Task Lane preview",
        "status": "preview",
        "notes": "No scheduler, background jobs, task execution, notifications, or task persistence.",
    },
    {
        "id": "guardian-controls",
        "label": "Guardian Controls shell",
        "status": "preview",
        "notes": "No policy enforcement runtime.",
    },
    {
        "id": "desktop-packaging",
        "label": "Desktop packaging",
        "status": "planned",
        "notes": "No installer or desktop binary yet.",
    },
    {
        "id": "connectors",
        "label": "Connectors",
        "status": "guarded-future",
        "notes": "No connector calls or external sends.",
    },
    {
        "id": "model-calls",
        "label": "Cloud model calls",
        "status": "guarded-future",
        "notes": "No cloud provider runtime or production model routing.",
    },
    {
        "id": "credential-storage",
        "label": "Credential storage",
        "status": "guarded-future",
        "notes": "No credential entry or storage path.",
    },
    {
        "id": "tool-execution",
        "label": "Tool execution",
        "status": "guarded-future",
        "notes": "No terminal, tool, or automation execution.",
    },
]


@router.get("/capabilities")
def capabilities() -> CapabilitiesResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "capabilities": CAPABILITIES,
    }
