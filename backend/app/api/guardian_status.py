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


class ProviderAdapterContract(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    contract_version: int
    dispatch: str
    provider_ids: list[str]
    required_request_fields: list[str]
    allowed_response_statuses: list[str]
    audit: str
    documentation: str
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
    provider_adapter_contract: ProviderAdapterContract
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
    "blocked_until": "Codex and Claude subscription CLI dispatch requires a configured localhost LIMA Guardian provider adapter.",
    "notes": "Sparkbot may report subscription sign-in readiness and can delegate explicit provider prompts to a configured localhost LIMA Guardian adapter, but direct Codex or Claude CLI execution remains disabled in Sparkbot.",
}


PROVIDER_ADAPTER_CONTRACT: ProviderAdapterContract = {
    "id": "lima-guardian-provider-adapter-contract",
    "label": "LIMA Guardian provider adapter contract",
    "status": "guarded-future",
    "contract_version": 1,
    "dispatch": "delegated-fail-closed",
    "provider_ids": ["openai-codex-subscription", "claude-subscription"],
    "required_request_fields": [
        "contract_version",
        "request_id",
        "provider_id",
        "model",
        "prompt",
        "operator_approval",
        "limits",
        "audit",
    ],
    "allowed_response_statuses": ["succeeded", "denied", "blocked", "timeout", "failed"],
    "audit": "required-before-final",
    "documentation": "docs/LIMA_PROVIDER_GUARDIAN_ADAPTER.md",
    "notes": "Read-only contract metadata plus fail-closed Sparkbot client requirements for guarded subscription dispatch; no adapter runtime or CLI dispatch is implemented in Sparkbot.",
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
        "notes": "Automatic or Guardian-mediated model provider calls remain guarded future; explicit env-enabled provider prompt smokes are separate operator-initiated calls.",
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
        "provider_adapter_contract": PROVIDER_ADAPTER_CONTRACT,
        "sensitive_action_categories": SENSITIVE_ACTION_CATEGORIES,
    }


assert {category["status"] for category in SENSITIVE_ACTION_CATEGORIES} <= ALLOWED_CAPABILITY_STATUSES
assert PROVIDER_EXECUTION_BOUNDARY["status"] in ALLOWED_CAPABILITY_STATUSES
assert PROVIDER_ADAPTER_CONTRACT["status"] in ALLOWED_CAPABILITY_STATUSES
