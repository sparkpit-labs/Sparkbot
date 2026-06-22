from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.services import provider_runtime
from app.services.provider_runtime import ProviderConfigError, ProviderUnavailableError

router = APIRouter()


class ProviderPromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    model: str | None = Field(default=None, min_length=1, max_length=160)


@router.get("/provider-config/status")
def provider_config_status() -> provider_runtime.ProviderConfigStatusResponse:
    return provider_runtime.get_provider_config_status()


@router.post("/provider-config/openrouter/prompt")
def run_openrouter_prompt(payload: ProviderPromptRequest) -> dict:
    if not provider_runtime.provider_calls_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provider prompt calls are disabled. Set SPARKBOT_PROVIDER_CALLS_ENABLED=true to enable explicit OpenRouter prompt calls.",
        )
    try:
        return provider_runtime.run_openrouter_prompt(payload.prompt, payload.model)
    except ProviderConfigError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


assert {provider["status"] for provider in provider_runtime.get_provider_config_status()["providers"]} <= ALLOWED_CAPABILITY_STATUSES
