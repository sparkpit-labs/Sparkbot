from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Literal

import os

import httpx

from app.api.command_center import (
    MODEL_LABELS,
    PROVIDER_ENV_KEYS,
    _configured_provider,
    _provider_for_model,
    _read_config,
    _read_secrets,
)
from app.services.workstation_store import WorkstationStore


ModelStatus = Literal["success", "unconfigured", "unsupported", "error", "timeout"]

OPENAI_COMPATIBLE_ENDPOINTS = {
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "xai": "https://api.x.ai/v1/chat/completions",
}
SUPPORTED_PROVIDERS = set(OPENAI_COMPATIBLE_ENDPOINTS) | {"anthropic", "google", "ollama"}
SUBSCRIPTION_ONLY_PROVIDERS = {"openai_codex", "claude_sub"}


@dataclass(frozen=True)
class ModelRoute:
    provider: str
    model: str
    label: str
    configured: bool
    base_url: str
    api_key: str = ""
    auth_mode: str = "api_key"


@dataclass(frozen=True)
class ModelExecutionResult:
    status: ModelStatus
    provider: str
    model: str
    label: str
    text: str = ""
    error: str = ""
    event_id: str = ""
    duration_ms: int = 0

    @property
    def ok(self) -> bool:
        return self.status == "success" and bool(self.text.strip())


def resolve_model_route(route: dict[str, Any] | None = None) -> ModelRoute:
    config = _read_config()
    secrets_payload = _read_secrets()
    default = config.get("default_selection") if isinstance(config.get("default_selection"), dict) else {}
    local_runtime = config.get("local_runtime") if isinstance(config.get("local_runtime"), dict) else {}
    requested = route or {}

    model = str(requested.get("model") or default.get("model") or "").strip()
    provider = str(requested.get("provider") or default.get("provider") or "").strip()
    api_key = str(requested.get("api_key") or "").strip()
    auth_mode = str(requested.get("auth_mode") or "api_key").strip().lower() or "api_key"
    if not model or model == "local-workstation":
        model = str(default.get("model") or "").strip()
    if provider in {"", "default"}:
        provider = _provider_for_model(model) or str(default.get("provider") or "").strip()
    if provider == "local":
        provider = "ollama"

    model_provider = _provider_for_model(model)
    if model_provider and provider != model_provider:
        provider = model_provider

    configured = bool(api_key) or _configured_provider(provider, secrets_payload)
    return ModelRoute(
        provider=provider or "local",
        model=model or "local-workstation",
        label=MODEL_LABELS.get(model, model or "Local Workstation"),
        configured=configured,
        base_url=str(local_runtime.get("base_url") or "http://127.0.0.1:11434").rstrip("/"),
        api_key=api_key,
        auth_mode=auth_mode,
    )


async def execute_model_request(
    *,
    route: dict[str, Any] | None,
    messages: list[dict[str, str]],
    store: WorkstationStore,
    surface: str,
    source_id: str,
    actor: str = "sparkbot",
    timeout_seconds: float = 20.0,
    event_metadata: dict[str, Any] | None = None,
) -> ModelExecutionResult:
    resolved = resolve_model_route(route)
    started = perf_counter()
    status: ModelStatus = "error"
    text = ""
    error = ""
    http_status: int | None = None

    try:
        if resolved.provider in SUBSCRIPTION_ONLY_PROVIDERS or resolved.provider not in SUPPORTED_PROVIDERS:
            status = "unsupported"
            error = "Selected provider route is not available for server-side model execution in this public slice."
        elif not resolved.configured:
            status = "unconfigured"
            error = "Selected provider is not configured server-side."
        else:
            payload = await _dispatch_provider_request(resolved, messages, timeout_seconds)
            text = _extract_response_text(resolved.provider, payload).strip()
            if text:
                status = "success"
            else:
                status = "error"
                error = "Provider returned an empty response."
    except httpx.TimeoutException:
        status = "timeout"
        error = "Provider request timed out."
    except httpx.HTTPStatusError as exc:
        status = "error"
        http_status = exc.response.status_code if exc.response is not None else None
        error = "Provider request failed."
    except httpx.RequestError:
        status = "error"
        error = "Provider request failed."
    except ValueError as exc:
        status = "error"
        error = str(exc)

    duration_ms = max(0, int((perf_counter() - started) * 1000))
    event = _log_model_event(
        store=store,
        surface=surface,
        source_id=source_id,
        actor=actor,
        provider=resolved.provider,
        model=resolved.model,
        status=status,
        message_count=len(messages),
        output_chars=len(text),
        duration_ms=duration_ms,
        error=error,
        http_status=http_status,
        event_metadata=event_metadata,
    )
    return ModelExecutionResult(
        status=status,
        provider=resolved.provider,
        model=resolved.model,
        label=resolved.label,
        text=text if status == "success" else "",
        error=error,
        event_id=str(event.get("id") or ""),
        duration_ms=duration_ms,
    )


async def _dispatch_provider_request(route: ModelRoute, messages: list[dict[str, str]], timeout_seconds: float) -> dict[str, Any]:
    if route.provider in OPENAI_COMPATIBLE_ENDPOINTS:
        return await _post_json(
            OPENAI_COMPATIBLE_ENDPOINTS[route.provider],
            _bearer_headers(route.provider, route.api_key),
            {
                "model": _provider_model_id(route.provider, route.model),
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 800,
            },
            timeout_seconds,
        )
    if route.provider == "anthropic":
        system_prompt = "\n\n".join(item["content"] for item in messages if item.get("role") == "system")
        anthropic_messages = [
            {"role": item.get("role") if item.get("role") in {"user", "assistant"} else "user", "content": item.get("content", "")}
            for item in messages
            if item.get("role") != "system"
        ]
        payload: dict[str, Any] = {
            "model": _provider_model_id(route.provider, route.model),
            "messages": anthropic_messages,
            "max_tokens": 800,
        }
        if system_prompt:
            payload["system"] = system_prompt
        return await _post_json(
            "https://api.anthropic.com/v1/messages",
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                **_anthropic_auth_headers(route.api_key, route.auth_mode),
                "anthropic-version": "2023-06-01",
            },
            payload,
            timeout_seconds,
        )
    if route.provider == "google":
        system_prompt = "\n\n".join(item["content"] for item in messages if item.get("role") == "system")
        user_text = "\n\n".join(item["content"] for item in messages if item.get("role") != "system")
        payload = {"contents": [{"role": "user", "parts": [{"text": user_text}]}]}
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        model = _provider_model_id(route.provider, route.model)
        provider_key = route.api_key or _provider_api_key(route.provider)
        return await _post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={provider_key}",
            {"Accept": "application/json", "Content-Type": "application/json"},
            payload,
            timeout_seconds,
        )
    if route.provider == "ollama":
        return await _post_json(
            f"{route.base_url}/api/chat",
            {"Accept": "application/json", "Content-Type": "application/json"},
            {"model": _provider_model_id(route.provider, route.model), "messages": messages, "stream": False},
            timeout_seconds,
        )
    raise ValueError("Selected provider is not supported.")


async def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Provider returned an invalid response.")
    return data


def _provider_api_key(provider: str) -> str:
    env_key = PROVIDER_ENV_KEYS.get(provider, "")
    secrets_payload = _read_secrets()
    return (os.getenv(env_key, "").strip() if env_key else "") or secrets_payload.get(provider, "")


def _bearer_headers(provider: str, api_key: str = "") -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key or _provider_api_key(provider)}",
    }


def _anthropic_auth_headers(api_key: str = "", auth_mode: str = "api_key") -> dict[str, str]:
    credential = api_key or _provider_api_key("anthropic")
    if api_key and auth_mode == "oauth":
        return {"Authorization": f"Bearer {credential}", "anthropic-beta": "oauth-2025-04-20"}
    return {"x-api-key": credential}


def _provider_model_id(provider: str, model: str) -> str:
    if provider == "openrouter" and model.startswith("openrouter/"):
        return model.split("/", 1)[1]
    if provider == "ollama" and model.startswith("ollama/"):
        return model.split("/", 1)[1]
    for prefix_provider, prefix in (("google", "gemini/"), ("groq", "groq/"), ("minimax", "minimax/"), ("xai", "xai/")):
        if provider == prefix_provider and model.startswith(prefix):
            return model.split("/", 1)[1]
    return model


def _extract_response_text(provider: str, payload: dict[str, Any]) -> str:
    if provider in OPENAI_COMPATIBLE_ENDPOINTS:
        choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
        first = choices[0] if choices else {}
        message = first.get("message") if isinstance(first, dict) else {}
        content = message.get("content") if isinstance(message, dict) else ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(str(part.get("text") or "") for part in content if isinstance(part, dict))
    if provider == "anthropic":
        content = payload.get("content") if isinstance(payload.get("content"), list) else []
        return "\n".join(str(part.get("text") or "") for part in content if isinstance(part, dict))
    if provider == "google":
        candidates = payload.get("candidates") if isinstance(payload.get("candidates"), list) else []
        first = candidates[0] if candidates else {}
        content = first.get("content") if isinstance(first, dict) else {}
        parts = content.get("parts") if isinstance(content, dict) and isinstance(content.get("parts"), list) else []
        return "\n".join(str(part.get("text") or "") for part in parts if isinstance(part, dict))
    if provider == "ollama":
        message = payload.get("message") if isinstance(payload.get("message"), dict) else {}
        if isinstance(message.get("content"), str):
            return message["content"]
        if isinstance(payload.get("response"), str):
            return payload["response"]
    return ""


def _log_model_event(
    *,
    store: WorkstationStore,
    surface: str,
    source_id: str,
    actor: str,
    provider: str,
    model: str,
    status: ModelStatus,
    message_count: int,
    output_chars: int,
    duration_ms: int,
    error: str,
    http_status: int | None,
    event_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "provider": provider,
        "model": model,
        "status": status,
        "message_count": message_count,
        "output_chars": output_chars,
        "duration_ms": duration_ms,
    }
    if error:
        payload["error"] = error
    if http_status:
        payload["http_status"] = http_status
    if event_metadata:
        for key, value in event_metadata.items():
            if key not in payload:
                payload[key] = value
    return store.append_event(
        {
            "event_type": "model.call.completed" if status == "success" else "model.call.failed",
            "surface": surface,
            "source_id": source_id,
            "summary": "Model call completed." if status == "success" else "Model call failed safely.",
            "payload": payload,
        },
        actor=actor,
    )
