from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

ImplementationStatus = Literal["not-implemented"]
AuditTrailStatus = Literal["planned"]
DefaultPosture = Literal["deny-sensitive-actions"]


class SensitiveActionCategory(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class ProviderExecutionBoundary(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    runtime_gate: str
    dispatch: str
    required_controls: list[str]
    blocked_until: str
    notes: str


class GuardianStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    runtime_enforcement: ImplementationStatus
    approval_tokens: ImplementationStatus
    policy_decisions: ImplementationStatus
    audit_trail: AuditTrailStatus
    default_posture: DefaultPosture
    provider_execution_boundary: ProviderExecutionBoundary
    sensitive_action_categories: list[SensitiveActionCategory]


PROVIDER_EXECUTION_BOUNDARY: ProviderExecutionBoundary = {
    "id": "lima-guardian-provider-runtime",
    "label": "LIMA Guardian provider runtime boundary",
    "status": "guarded-future",
    "runtime_gate": "lima-guardian-required",
    "dispatch": "fail-closed",
    "required_controls": [
        "capability-check",
        "operator-approval",
        "audit-log",
        "secret-redaction",
        "timeout",
        "no-shell-expansion",
    ],
    "blocked_until": "Codex and Claude subscription CLI dispatch requires a LIMA Guardian execution adapter.",
    "notes": "Sparkbot may report subscription sign-in readiness, but direct Codex or Claude CLI execution remains disabled until LIMA provides guarded dispatch with audit and fail-closed behavior.",
}


SENSITIVE_ACTION_CATEGORIES: list[SensitiveActionCategory] = [
    {
        "id": "external-sends",
        "label": "External sends",
        "status": "guarded-future",
        "notes": "No external sends are implemented.",
    },
    {
        "id": "connector-calls",
        "label": "Connector calls",
        "status": "guarded-future",
        "notes": "No connector calls are implemented.",
    },
    {
        "id": "credential-use",
        "label": "Credential use",
        "status": "guarded-future",
        "notes": "No credential use or storage is implemented.",
    },
    {
        "id": "model-provider-calls",
        "label": "Model provider calls",
        "status": "guarded-future",
        "notes": "No model provider calls are implemented.",
    },
    {
        "id": "file-writes",
        "label": "File writes",
        "status": "guarded-future",
        "notes": "No file mutation workflow is implemented.",
    },
    {
        "id": "tool-execution",
        "label": "Tool execution",
        "status": "guarded-future",
        "notes": "No terminal or tool execution is implemented.",
    },
]


@router.get("/guardian/status")
def guardian_status() -> GuardianStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "preview",
        "runtime_enforcement": "not-implemented",
        "approval_tokens": "not-implemented",
        "policy_decisions": "not-implemented",
        "audit_trail": "planned",
        "default_posture": "deny-sensitive-actions",
        "provider_execution_boundary": PROVIDER_EXECUTION_BOUNDARY,
        "sensitive_action_categories": SENSITIVE_ACTION_CATEGORIES,
    }


assert {category["status"] for category in SENSITIVE_ACTION_CATEGORIES} <= ALLOWED_CAPABILITY_STATUSES
assert PROVIDER_EXECUTION_BOUNDARY["status"] in ALLOWED_CAPABILITY_STATUSES
