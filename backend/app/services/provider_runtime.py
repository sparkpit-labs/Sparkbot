from __future__ import annotations

import os
import pathlib
import re
import shutil
from typing import Any, Literal, TypedDict

import httpx

from app.api.capabilities import CapabilityStatus
from app.services import local_model_adapter

ENABLE_VALUES = {"1", "true", "yes", "on"}
OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_FREE_MODEL = "meta-llama/llama-3.2-3b-instruct:free"
OPENROUTER_TIMEOUT_SECONDS = 30
MODEL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")

ProviderImplementationStatus = Literal["not-implemented", "env-driven", "disabled-by-default", "guarded-manual"]


class ProviderRuntimeError(RuntimeError):
    pass


class ProviderConfigError(ProviderRuntimeError):
    pass


class ProviderUnavailableError(ProviderRuntimeError):
    pass


class ProviderStatus(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    configured: bool
    auth_mode: str
    configuration: str
    credential_source: str
    default_model: str | None
    model_examples: list[str]
    runtime: str
    notes: str


class ProviderConfigStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    credential_storage: ProviderImplementationStatus
    provider_calls: ProviderImplementationStatus
    model_routing: ProviderImplementationStatus
    providers: list[ProviderStatus]


API_KEY_PROVIDERS = [
    {
        "id": "openrouter",
        "label": "OpenRouter",
        "env": "OPENROUTER_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_OPENROUTER_MODEL",
        "default_model": DEFAULT_OPENROUTER_FREE_MODEL,
        "examples": [
            DEFAULT_OPENROUTER_FREE_MODEL,
            "mistralai/mistral-7b-instruct:free",
            "openrouter/openai/gpt-4o-mini:free",
        ],
        "runtime": "Guarded backend prompt endpoint for explicit operator calls. Free :free models are enforced by default.",
        "notes": "Uses OpenRouter through a backend-only env key. Set SPARKBOT_PROVIDER_CALLS_ENABLED=true to enable explicit OpenRouter prompt calls.",
    },
    {
        "id": "openai",
        "label": "OpenAI API",
        "env": "OPENAI_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_OPENAI_MODEL",
        "default_model": "gpt-5-mini",
        "examples": ["gpt-5-mini", "gpt-5.3-codex", "codex-mini-latest"],
        "runtime": "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
        "notes": "Matches the prototype provider slot for OpenAI API keys without adding browser credential entry or storage.",
    },
    {
        "id": "anthropic",
        "label": "Anthropic API",
        "env": "ANTHROPIC_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_ANTHROPIC_MODEL",
        "default_model": "claude-sonnet-4-5",
        "examples": ["claude-sonnet-4-5", "claude-haiku-4-5", "claude-opus-4-6"],
        "runtime": "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
        "notes": "Matches the prototype Anthropic provider slot without adding browser credential entry or storage.",
    },
    {
        "id": "google",
        "label": "Google Gemini API",
        "env": "GOOGLE_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_GOOGLE_MODEL",
        "default_model": "gemini/gemini-2.0-flash",
        "examples": ["gemini/gemini-2.0-flash", "gemini/gemini-3-flash"],
        "runtime": "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
        "notes": "Matches the prototype Google provider slot without adding browser credential entry or storage.",
    },
    {
        "id": "groq",
        "label": "Groq API",
        "env": "GROQ_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_GROQ_MODEL",
        "default_model": "groq/llama-3.3-70b-versatile",
        "examples": ["groq/llama-3.3-70b-versatile"],
        "runtime": "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
        "notes": "Matches the prototype Groq provider slot without adding browser credential entry or storage.",
    },
    {
        "id": "minimax",
        "label": "MiniMax API",
        "env": "MINIMAX_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_MINIMAX_MODEL",
        "default_model": "minimax/MiniMax-M2.5",
        "examples": ["minimax/MiniMax-M2.5"],
        "runtime": "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
        "notes": "Matches the prototype MiniMax provider slot without adding browser credential entry or storage.",
    },
    {
        "id": "xai",
        "label": "xAI API",
        "env": "XAI_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_XAI_MODEL",
        "default_model": "xai/grok-4",
        "examples": ["xai/grok-4", "xai/grok-3-mini"],
        "runtime": "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
        "notes": "Matches the prototype xAI provider slot without adding browser credential entry or storage.",
    },
]


def env_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ENABLE_VALUES


def provider_calls_enabled() -> bool:
    return env_enabled("SPARKBOT_PROVIDER_CALLS_ENABLED")


def paid_openrouter_models_enabled() -> bool:
    return env_enabled("SPARKBOT_ALLOW_PAID_OPENROUTER_MODELS")


def _env_has_value(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


def _configured_model(env_name: str, fallback: str | None) -> str | None:
    value = os.environ.get(env_name, "").strip()
    return value or fallback


def _provider_status_from_env(item: dict[str, Any]) -> ProviderStatus:
    configured = _env_has_value(str(item["env"]))
    calls_enabled = provider_calls_enabled()
    provider_id = str(item["id"])
    status: CapabilityStatus
    if provider_id == "openrouter" and configured and calls_enabled:
        status = "available"
    elif configured:
        status = "disabled-by-default"
    else:
        status = "planned"
    return {
        "id": provider_id,
        "label": str(item["label"]),
        "status": status,
        "configured": configured,
        "auth_mode": str(item["auth_mode"]),
        "configuration": "environment",
        "credential_source": str(item["env"]),
        "default_model": _configured_model(str(item["default_model_env"]), item.get("default_model")),
        "model_examples": list(item["examples"]),
        "runtime": str(item["runtime"]),
        "notes": str(item["notes"]),
    }


def _codex_auth_file_exists() -> bool:
    override = os.environ.get("SPARKBOT_CODEX_AUTH_FILE", "").strip()
    if override:
        return pathlib.Path(override).expanduser().is_file()
    codex_home = pathlib.Path(os.environ.get("CODEX_HOME", str(pathlib.Path.home() / ("." + "codex")))).expanduser()
    return (codex_home / "auth.json").is_file()


def _codex_cli_available() -> bool:
    configured = os.environ.get("SPARKBOT_CODEX_CLI", "").strip()
    if configured:
        return pathlib.Path(configured).expanduser().is_file() or shutil.which(configured) is not None
    return shutil.which("codex") is not None


def _claude_cli_available() -> bool:
    configured = os.environ.get("SPARKBOT_CLAUDE_CLI", "").strip()
    if configured:
        return pathlib.Path(configured).expanduser().is_file() or shutil.which(configured) is not None
    return shutil.which("claude") is not None


def _claude_subscription_hint_present() -> bool:
    if env_enabled("SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED"):
        return True
    return pathlib.Path.home().joinpath("." + "claude").exists()


def _subscription_statuses() -> list[ProviderStatus]:
    codex_configured = _codex_auth_file_exists() and _codex_cli_available()
    claude_configured = _claude_subscription_hint_present() and _claude_cli_available()
    return [
        {
            "id": "openai-codex-subscription",
            "label": "OpenAI Codex Subscription",
            "status": "disabled-by-default" if codex_configured else "planned",
            "configured": codex_configured,
            "auth_mode": "codex-cli-sign-in",
            "configuration": "local-cli-sign-in",
            "credential_source": "CODEX_HOME auth file",
            "default_model": os.environ.get("SPARKBOT_CODEX_MODEL", "openai-codex/gpt-5.3-codex").strip(),
            "model_examples": ["openai-codex/gpt-5.3-codex", "openai-codex/gpt-5.5", "openai-codex/gpt-5.4"],
            "runtime": "Sign-in detection only in this public branch. CLI dispatch requires the LIMA Guardian execution boundary.",
            "notes": "Run codex login with a ChatGPT/Codex subscription, then restart Sparkbot. Auth presence is detected without reading or returning the auth file.",
        },
        {
            "id": "claude-subscription",
            "label": "Claude Subscription",
            "status": "disabled-by-default" if claude_configured else "planned",
            "configured": claude_configured,
            "auth_mode": "claude-cli-sign-in",
            "configuration": "local-cli-sign-in",
            "credential_source": "Claude Code local sign-in",
            "default_model": os.environ.get("SPARKBOT_CLAUDE_SUB_MODEL", "claude-sub/sonnet").strip(),
            "model_examples": ["claude-sub/sonnet", "claude-sub/opus", "claude-sub/haiku", "claude-sub/opus-1m"],
            "runtime": "Sign-in detection only in this public branch. CLI dispatch requires the LIMA Guardian execution boundary.",
            "notes": "Install Claude Code, sign in locally, and set SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true when using this public shell status path.",
        },
    ]


def _local_provider_status() -> ProviderStatus:
    local_status = local_model_adapter.get_ollama_status()
    enabled = bool(local_status.get("local_models_enabled"))
    available = local_status.get("status") == "available-local-only"
    return {
        "id": "local-ollama",
        "label": "Local Ollama",
        "status": "available" if available else "disabled-by-default",
        "configured": enabled,
        "auth_mode": "none",
        "configuration": "environment-localhost",
        "credential_source": "not-required",
        "default_model": local_status.get("configured_model"),
        "model_examples": ["llama3.2", "qwen2.5-coder", "mistral"],
        "runtime": "Active localhost-only adapter when SPARKBOT_LOCAL_MODELS_ENABLED=true and Ollama is reachable.",
        "notes": "Uses only localhost or 127.0.0.1. No cloud provider credentials are used.",
    }


def get_provider_config_status() -> ProviderConfigStatusResponse:
    calls_enabled = provider_calls_enabled()
    providers = [_local_provider_status(), *[_provider_status_from_env(item) for item in API_KEY_PROVIDERS], *_subscription_statuses()]
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "available" if calls_enabled else "disabled-by-default",
        "credential_storage": "not-implemented",
        "provider_calls": "guarded-manual" if calls_enabled else "disabled-by-default",
        "model_routing": "env-driven",
        "providers": providers,
    }


def validate_openrouter_model(model: str) -> str:
    model = model.strip()
    if not MODEL_NAME_PATTERN.fullmatch(model):
        raise ProviderConfigError("OpenRouter model must be a safe model identifier.")
    if not model.endswith(":free") and not paid_openrouter_models_enabled():
        raise ProviderConfigError(
            "OpenRouter prompt calls default to free models only. Use a model ending in :free or explicitly enable paid OpenRouter models."
        )
    return model


def _openrouter_model_for_api(model: str) -> str:
    normalized = model.removeprefix("openrouter/")
    return normalized


def get_openrouter_model(model: str | None = None) -> str:
    selected = (model or os.environ.get("SPARKBOT_OPENROUTER_MODEL") or DEFAULT_OPENROUTER_FREE_MODEL).strip()
    return validate_openrouter_model(selected)


def run_openrouter_prompt(prompt: str, model: str | None = None) -> dict[str, Any]:
    prompt = prompt.strip()
    if not prompt:
        raise ProviderConfigError("Prompt is required.")
    if not provider_calls_enabled():
        raise ProviderConfigError("Provider prompt calls are disabled.")
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ProviderConfigError("OpenRouter is not configured. Set OPENROUTER_API_KEY before enabling OpenRouter prompt calls.")
    selected_model = get_openrouter_model(model)
    request_model = _openrouter_model_for_api(selected_model)
    payload = {
        "model": request_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    data = _post_openrouter_chat(payload, api_key)
    response_text = _extract_openrouter_response(data)
    return {
        "provider": "openrouter",
        "model": selected_model,
        "request_model": request_model,
        "response": response_text,
        "usage": data.get("usage") if isinstance(data.get("usage"), dict) else None,
    }


def _post_openrouter_chat(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-Title": "Sparkbot Public",
    }
    try:
        with httpx.Client(timeout=OPENROUTER_TIMEOUT_SECONDS, follow_redirects=False) as client:
            response = client.post(OPENROUTER_CHAT_COMPLETIONS_URL, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise ProviderUnavailableError("OpenRouter endpoint is unavailable.") from exc
    if response.status_code >= 400:
        raise ProviderUnavailableError(f"OpenRouter request failed with status {response.status_code}.")
    try:
        data = response.json()
    except ValueError as exc:
        raise ProviderUnavailableError("OpenRouter returned invalid JSON.") from exc
    if not isinstance(data, dict):
        raise ProviderUnavailableError("OpenRouter returned an unexpected response.")
    return data


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts).strip()
    return ""


def _extract_openrouter_response(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderUnavailableError("OpenRouter returned no choices.")
    first = choices[0]
    if not isinstance(first, dict):
        raise ProviderUnavailableError("OpenRouter returned an unexpected choice.")
    message = first.get("message")
    if not isinstance(message, dict):
        raise ProviderUnavailableError("OpenRouter returned an unexpected message.")
    text = _content_to_text(message.get("content"))
    if not text:
        raise ProviderUnavailableError("OpenRouter returned an empty response.")
    return text
