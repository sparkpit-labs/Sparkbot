from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

ImplementationStatus = Literal["not-implemented"]
AuditTrailStatus = Literal["planned"]


class ConnectorStatus(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class ConnectorStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    connectors_enabled: bool
    outbound_actions: ImplementationStatus
    credential_storage: ImplementationStatus
    audit_trail: AuditTrailStatus
    connectors: list[ConnectorStatus]


CONNECTORS: list[ConnectorStatus] = [
    {
        "id": "messaging",
        "label": "Messaging connectors",
        "status": "guarded-future",
        "notes": "Messaging connectors are planned for future guarded configuration. No outbound sends are implemented.",
    },
    {
        "id": "calendar",
        "label": "Calendar connectors",
        "status": "guarded-future",
        "notes": "Calendar connectors are planned for future guarded configuration.",
    },
    {
        "id": "email",
        "label": "Email connectors",
        "status": "guarded-future",
        "notes": "Email connectors are planned for future guarded configuration. No external sends are implemented.",
    },
    {
        "id": "files",
        "label": "File connectors",
        "status": "guarded-future",
        "notes": "File connectors are planned for future guarded configuration. No file mutation is implemented.",
    },
]


@router.get("/connector-status")
def connector_status() -> ConnectorStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "guarded-future",
        "connectors_enabled": False,
        "outbound_actions": "not-implemented",
        "credential_storage": "not-implemented",
        "audit_trail": "planned",
        "connectors": CONNECTORS,
    }


assert {connector["status"] for connector in CONNECTORS} <= ALLOWED_CAPABILITY_STATUSES
