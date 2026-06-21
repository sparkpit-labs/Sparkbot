from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services import local_model_adapter
from app.services.local_model_adapter import LocalModelConfigError, LocalModelUnavailableError
from app.services.local_workstation_store import LocalStoreError, LocalWorkstationStore, NotFoundError

router = APIRouter(prefix="/local-models", tags=["local-models"])

MAX_SELECTED_MEMORY_NOTES = 8
MAX_MEMORY_CONTEXT_CHARS = 4000


class LocalPromptRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1, max_length=120)
    prompt: str = Field(min_length=1, max_length=8000)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    selected_memory_note_ids: list[str] = Field(default_factory=list, max_length=MAX_SELECTED_MEMORY_NOTES)


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
        store = LocalWorkstationStore() if payload.session_id or payload.selected_memory_note_ids else None
        selected_memory_notes = _load_selected_memory_notes(store, payload.selected_memory_note_ids)
        prompt = _compose_prompt_with_selected_memory_notes(payload.prompt, selected_memory_notes)
        result = local_model_adapter.run_ollama_prompt(prompt, payload.model)
        stored_message = None
        if payload.session_id:
            stored_message = store.add_chat_message(payload.session_id, "assistant-local", result["response"])
        return {
            **result,
            "stored_message": stored_message,
            "memory_context": "explicit-selected" if selected_memory_notes else "none",
            "selected_memory_note_count": len(selected_memory_notes),
        }
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (LocalModelConfigError, LocalStoreError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LocalModelUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


def _load_selected_memory_notes(store: LocalWorkstationStore | None, note_ids: list[str]) -> list[dict[str, Any]]:
    normalized_ids = [note_id.strip() for note_id in note_ids]
    if not normalized_ids:
        return []
    if any(not note_id for note_id in normalized_ids):
        raise LocalStoreError("selected_memory_note_ids cannot include blank values")
    if len(set(normalized_ids)) != len(normalized_ids):
        raise LocalStoreError("selected_memory_note_ids cannot include duplicates")
    if store is None:
        store = LocalWorkstationStore()
    return [store.get_memory_note(note_id) for note_id in normalized_ids]


def _compose_prompt_with_selected_memory_notes(prompt: str, notes: list[dict[str, Any]]) -> str:
    if not notes:
        return prompt

    remaining = MAX_MEMORY_CONTEXT_CHARS
    context_blocks: list[str] = []
    for note in notes:
        block = f"Title: {note['title']}\nBody: {note['body']}"
        if len(block) > remaining:
            block = block[:remaining].rstrip()
        if block:
            context_blocks.append(block)
            remaining -= len(block)
        if remaining <= 0:
            break

    context = "\n\n---\n\n".join(context_blocks)
    return (
        "Selected local memory notes were explicitly included by the operator.\n\n"
        f"{context}\n\n"
        "Operator prompt:\n"
        f"{prompt}"
    )
