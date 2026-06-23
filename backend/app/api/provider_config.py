from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, ValidationError

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.services import provider_runtime
from app.services.provider_runtime import ProviderConfigError, ProviderNotFoundError, ProviderUnavailableError

router = APIRouter()


class ProviderPromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    model: str | None = Field(default=None, min_length=1, max_length=160)


@router.get("/provider-config/status")
def provider_config_status() -> provider_runtime.ProviderConfigStatusResponse:
    return provider_runtime.get_provider_config_status()


@router.post("/provider-config/{provider_id}/prompt")
def run_provider_prompt(provider_id: str, payload: dict) -> dict:
    if not provider_runtime.provider_prompt_supported(provider_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_id} is not an API-key prompt provider.",
        )
    if not provider_runtime.provider_calls_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provider prompt calls are disabled. Set SPARKBOT_PROVIDER_CALLS_ENABLED=true to enable explicit provider prompt calls.",
        )
    try:
        request = ProviderPromptRequest.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc
    try:
        return provider_runtime.run_provider_prompt(provider_id, request.prompt, request.model)
    except ProviderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProviderConfigError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


assert {provider["status"] for provider in provider_runtime.get_provider_config_status()["providers"]} <= ALLOWED_CAPABILITY_STATUSES
