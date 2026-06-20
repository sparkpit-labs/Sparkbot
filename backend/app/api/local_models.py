from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services import local_model_adapter
from app.services.local_model_adapter import LocalModelConfigError, LocalModelUnavailableError
from app.services.local_workstation_store import LocalStoreError, LocalWorkstationStore, NotFoundError

router = APIRouter(prefix="/local-models", tags=["local-models"])


class LocalPromptRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1, max_length=120)
    prompt: str = Field(min_length=1, max_length=8000)
    model: str | None = Field(default=None, min_length=1, max_length=120)


@router.get("/status")
def local_model_status() -> dict:
    return local_model_adapter.get_ollama_status()


@router.post("/ollama/prompt")
def run_local_ollama_prompt(payload: LocalPromptRequest) -> dict:
    if not local_model_adapter.local_models_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Local model prompt calls are disabled. Set SPARKBOT_LOCAL_MODELS_ENABLED=true to enable localhost-only Ollama calls.",
        )
    try:
        result = local_model_adapter.run_ollama_prompt(payload.prompt, payload.model)
        stored_message = None
        if payload.session_id:
            stored_message = LocalWorkstationStore().add_chat_message(payload.session_id, "assistant-local", result["response"])
        return {**result, "stored_message": stored_message}
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (LocalModelConfigError, LocalStoreError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LocalModelUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
