from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

ImplementationStatus = Literal["not-implemented"]


class ProviderStatus(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class ProviderConfigStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    credential_storage: ImplementationStatus
    provider_calls: ImplementationStatus
    model_routing: ImplementationStatus
    providers: list[ProviderStatus]


PROVIDERS: list[ProviderStatus] = [
    {
        "id": "local",
        "label": "Local provider",
        "status": "planned",
        "notes": "Local provider configuration is planned. No runtime provider calls are made.",
    },
    {
        "id": "openai-compatible",
        "label": "OpenAI-compatible provider",
        "status": "guarded-future",
        "notes": "Cloud provider configuration will require explicit setup and safety gates.",
    },
    {
        "id": "anthropic-compatible",
        "label": "Anthropic-compatible provider",
        "status": "guarded-future",
        "notes": "Cloud provider configuration will require explicit setup and safety gates.",
    },
    {
        "id": "google-compatible",
        "label": "Google-compatible provider",
        "status": "guarded-future",
        "notes": "Cloud provider configuration will require explicit setup and safety gates.",
    },
    {
        "id": "custom-endpoint",
        "label": "Custom endpoint",
        "status": "guarded-future",
        "notes": "Custom endpoints are planned for future guarded configuration.",
    },
]


@router.get("/provider-config/status")
def provider_config_status() -> ProviderConfigStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "preview",
        "credential_storage": "not-implemented",
        "provider_calls": "not-implemented",
        "model_routing": "not-implemented",
        "providers": PROVIDERS,
    }


assert {provider["status"] for provider in PROVIDERS} <= ALLOWED_CAPABILITY_STATUSES
