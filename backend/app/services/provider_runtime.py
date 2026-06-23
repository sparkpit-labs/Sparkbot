from __future__ import annotations

import os
import pathlib
import re
import shutil
from typing import Any, Literal, NotRequired, TypedDict

import httpx

from app.api.capabilities import CapabilityStatus
from app.services import local_model_adapter

ENABLE_VALUES = {"1", "true", "yes", "on"}
OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
GOOGLE_GENERATE_CONTENT_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
MINIMAX_CHAT_COMPLETIONS_URL = "https://api.minimax.io/v1/chat/completions"
XAI_CHAT_COMPLETIONS_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_OPENROUTER_FREE_MODEL = "meta-llama/llama-3.2-3b-instruct:free"
OPENROUTER_TIMEOUT_SECONDS = 30
PROVIDER_TIMEOUT_SECONDS = 30
MODEL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")

ProviderImplementationStatus = Literal["not-implemented", "env-driven", "disabled-by-default", "guarded-manual"]


class ProviderRuntimeError(RuntimeError):
    pass


class ProviderConfigError(ProviderRuntimeError):
    pass


class ProviderUnavailableError(ProviderRuntimeError):
    pass


class ProviderNotFoundError(ProviderRuntimeError):
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
    cli_available: NotRequired[bool]
    sign_in_detected: NotRequired[bool]
    runtime_gate: NotRequired[str]
    operator_action: NotRequired[str]
    prompt_endpoint: NotRequired[str]
    prompt_adapter: NotRequired[str]


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
        "adapter": "openrouter-chat",
        "runtime": "Guarded backend prompt endpoint for explicit operator calls. Free :free models are enforced by default.",
        "notes": "Uses OpenRouter through a backend-only env key. Set SPARKBOT_PROVIDER_CALLS_ENABLED=true to enable explicit provider prompt calls.",
    },
    {
        "id": "openai",
        "label": "OpenAI API",
        "env": "OPENAI_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_OPENAI_MODEL",
        "default_model": "gpt-5-mini",
        "examples": ["gpt-5-mini", "gpt-5.3-codex", "codex-mini-latest"],
        "adapter": "openai-chat",
        "runtime": "Guarded backend prompt endpoint for explicit operator calls using the OpenAI Chat Completions API.",
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
        "adapter": "anthropic-messages",
        "runtime": "Guarded backend prompt endpoint for explicit operator calls using the Anthropic Messages API.",
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
        "adapter": "google-generate-content",
        "runtime": "Guarded backend prompt endpoint for explicit operator calls using the Google Gemini generateContent API.",
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
        "adapter": "groq-chat",
        "runtime": "Guarded backend prompt endpoint for explicit operator calls using Groq OpenAI-compatible chat completions.",
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
        "adapter": "minimax-chat",
        "base_url_env": "SPARKBOT_MINIMAX_CHAT_COMPLETIONS_URL",
        "runtime": "Guarded backend prompt endpoint for explicit operator calls using a MiniMax OpenAI-compatible chat adapter.",
        "notes": "Matches the prototype MiniMax provider slot without adding browser credential entry or storage. Set SPARKBOT_MINIMAX_CHAT_COMPLETIONS_URL to override the default endpoint if needed.",
    },
    {
        "id": "xai",
        "label": "xAI API",
        "env": "XAI_API_KEY",
        "auth_mode": "env-api-key",
        "default_model_env": "SPARKBOT_XAI_MODEL",
        "default_model": "xai/grok-4",
        "examples": ["xai/grok-4", "xai/grok-3-mini"],
        "adapter": "xai-chat",
        "runtime": "Guarded backend prompt endpoint for explicit operator calls using the xAI chat completions API.",
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


def _first_configured_env(names: list[str], fallback: str | None) -> str | None:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return fallback


def _provider_status_from_env(item: dict[str, Any]) -> ProviderStatus:
    configured = _env_has_value(str(item["env"]))
    calls_enabled = provider_calls_enabled()
    provider_id = str(item["id"])
    status: CapabilityStatus
    if configured and calls_enabled:
        status = "available"
    elif configured:
        status = "disabled-by-default"
    else:
        status = "planned"
    provider: ProviderStatus = {
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
        "prompt_endpoint": f"/provider-config/{provider_id}/prompt",
        "prompt_adapter": str(item["adapter"]),
    }
    return provider


def _codex_auth_file_exists() -> bool:
    override = os.environ.get("SPARKBOT_CODEX_AUTH_FILE", "").strip()
    if override:
        return pathlib.Path(override).expanduser().is_file()
    codex_home = pathlib.Path(os.environ.get("CODEX_HOME", str(pathlib.Path.home() / ("." + "codex")))).expanduser()
    return (codex_home / "auth.json").is_file()


def _common_cli_candidates(name: str) -> list[pathlib.Path]:
    home = pathlib.Path.home()
    return [
        home / ".local" / "bin" / name,
        home / "AppData" / "Roaming" / "npm" / f"{name}.cmd",
        home / "AppData" / "Roaming" / "npm" / f"{name}.ps1",
    ]


def _cli_available(env_name: str, executable: str) -> bool:
    configured = os.environ.get(env_name, "").strip()
    if configured:
        return pathlib.Path(configured).expanduser().is_file() or shutil.which(configured) is not None
    if shutil.which(executable) is not None:
        return True
    return any(candidate.is_file() for candidate in _common_cli_candidates(executable))


def _codex_cli_available() -> bool:
    return _cli_available("SPARKBOT_CODEX_CLI", "codex")


def _claude_cli_available() -> bool:
    return _cli_available("SPARKBOT_CLAUDE_CLI", "claude")


def _claude_subscription_hint_present() -> bool:
    if env_enabled("SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED"):
        return True
    override = os.environ.get("SPARKBOT_CLAUDE_AUTH_FILE", "").strip()
    if override:
        return pathlib.Path(override).expanduser().is_file()
    claude_home = pathlib.Path(os.environ.get("CLAUDE_HOME", str(pathlib.Path.home() / ("." + "claude")))).expanduser()
    return claude_home.exists()


def _subscription_statuses() -> list[ProviderStatus]:
    codex_cli_available = _codex_cli_available()
    codex_sign_in_detected = _codex_auth_file_exists()
    codex_configured = codex_cli_available and codex_sign_in_detected
    claude_cli_available = _claude_cli_available()
    claude_sign_in_detected = _claude_subscription_hint_present()
    claude_configured = claude_cli_available and claude_sign_in_detected
    return [
        {
            "id": "openai-codex-subscription",
            "label": "OpenAI Codex Subscription",
            "status": "disabled-by-default" if codex_configured else "planned",
            "configured": codex_configured,
            "auth_mode": "codex-cli-sign-in",
            "configuration": "local-cli-sign-in",
            "credential_source": "CODEX_HOME or SPARKBOT_CODEX_AUTH_FILE",
            "default_model": _first_configured_env(["SPARKBOT_CODEX_MODEL", "SPARKBOT_CODEX_SUBSCRIPTION_MODEL"], "openai-codex/gpt-5.3-codex"),
            "model_examples": ["openai-codex/gpt-5.3-codex", "openai-codex/gpt-5.5", "openai-codex/gpt-5.4"],
            "runtime": "Sign-in readiness only in this public branch. CLI dispatch requires the LIMA Guardian execution boundary.",
            "notes": "Run codex login with a ChatGPT/Codex subscription, then restart Sparkbot. Auth presence is detected without reading or returning the auth file.",
            "cli_available": codex_cli_available,
            "sign_in_detected": codex_sign_in_detected,
            "runtime_gate": "lima-guardian-required",
            "operator_action": _subscription_operator_action(
                cli_available=codex_cli_available,
                sign_in_detected=codex_sign_in_detected,
                install_action="Install the Codex CLI and make it available on PATH or SPARKBOT_CODEX_CLI.",
                sign_in_action="Run codex login, choose ChatGPT sign-in, then restart Sparkbot.",
            ),
        },
        {
            "id": "claude-subscription",
            "label": "Claude Subscription",
            "status": "disabled-by-default" if claude_configured else "planned",
            "configured": claude_configured,
            "auth_mode": "claude-cli-sign-in",
            "configuration": "local-cli-sign-in",
            "credential_source": "CLAUDE_HOME or SPARKBOT_CLAUDE_AUTH_FILE",
            "default_model": _first_configured_env(["SPARKBOT_CLAUDE_SUB_MODEL", "SPARKBOT_CLAUDE_SUBSCRIPTION_MODEL"], "claude-sub/sonnet"),
            "model_examples": ["claude-sub/sonnet", "claude-sub/opus", "claude-sub/haiku", "claude-sub/opus-1m"],
            "runtime": "Sign-in readiness only in this public branch. CLI dispatch requires the LIMA Guardian execution boundary.",
            "notes": "Install Claude Code and sign in locally. Sparkbot detects CLAUDE_HOME, SPARKBOT_CLAUDE_AUTH_FILE, or the operator-declared SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true flag without reading or returning auth contents.",
            "cli_available": claude_cli_available,
            "sign_in_detected": claude_sign_in_detected,
            "runtime_gate": "lima-guardian-required",
            "operator_action": _subscription_operator_action(
                cli_available=claude_cli_available,
                sign_in_detected=claude_sign_in_detected,
                install_action="Install Claude Code and make it available on PATH or SPARKBOT_CLAUDE_CLI.",
                sign_in_action="Sign in with Claude Code, set SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true if needed, then restart Sparkbot.",
            ),
        },
    ]


def _subscription_operator_action(*, cli_available: bool, sign_in_detected: bool, install_action: str, sign_in_action: str) -> str:
    if not cli_available:
        return install_action
    if not sign_in_detected:
        return sign_in_action
    return "Ready for LIMA Guardian runtime integration; direct CLI dispatch remains disabled in the public shell."


def _api_provider_by_id(provider_id: str) -> dict[str, Any] | None:
    normalized = provider_id.strip().lower()
    for item in API_KEY_PROVIDERS:
        if item["id"] == normalized:
            return item
    return None


def provider_prompt_supported(provider_id: str) -> bool:
    return _api_provider_by_id(provider_id) is not None


def _provider_api_key(provider: dict[str, Any]) -> str:
    return os.environ.get(str(provider["env"]), "").strip()


def _strip_provider_prefix(model: str, prefix: str) -> str:
    return model.removeprefix(prefix).strip()


def _selected_provider_model(provider: dict[str, Any], model: str | None = None) -> tuple[str, str]:
    selected = (model or os.environ.get(str(provider["default_model_env"])) or str(provider.get("default_model") or "")).strip()
    if not selected:
        raise ProviderConfigError(f"{provider['label']} model is required.")
    if not MODEL_NAME_PATTERN.fullmatch(selected):
        raise ProviderConfigError(f"{provider['label']} model must be a safe model identifier.")
    provider_id = str(provider["id"])
    if provider_id == "openrouter":
        selected = validate_openrouter_model(selected)
        return selected, _strip_provider_prefix(selected, "openrouter/")
    if provider_id == "google":
        return selected, _strip_provider_prefix(selected, "gemini/")
    if provider_id == "groq":
        return selected, _strip_provider_prefix(selected, "groq/")
    if provider_id == "minimax":
        return selected, _strip_provider_prefix(selected, "minimax/")
    if provider_id == "xai":
        return selected, _strip_provider_prefix(selected, "xai/")
    return selected, selected


def _post_provider_json(url: str, headers: dict[str, str], payload: dict[str, Any], provider_label: str) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=PROVIDER_TIMEOUT_SECONDS, follow_redirects=False) as client:
            response = client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise ProviderUnavailableError(f"{provider_label} endpoint is unavailable.") from exc
    if response.status_code >= 400:
        raise ProviderUnavailableError(f"{provider_label} request failed with status {response.status_code}.")
    try:
        data = response.json()
    except ValueError as exc:
        raise ProviderUnavailableError(f"{provider_label} returned invalid JSON.") from exc
    if not isinstance(data, dict):
        raise ProviderUnavailableError(f"{provider_label} returned an unexpected response.")
    return data


def _chat_headers(api_key: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-Title": "Sparkbot Public",
    }


def _extract_chat_completion_response(data: dict[str, Any], provider_label: str) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderUnavailableError(f"{provider_label} returned no choices.")
    first = choices[0]
    if not isinstance(first, dict):
        raise ProviderUnavailableError(f"{provider_label} returned an unexpected choice.")
    message = first.get("message")
    if not isinstance(message, dict):
        raise ProviderUnavailableError(f"{provider_label} returned an unexpected message.")
    text = _content_to_text(message.get("content"))
    if not text:
        raise ProviderUnavailableError(f"{provider_label} returned an empty response.")
    return text


def _extract_anthropic_response(data: dict[str, Any]) -> str:
    content = data.get("content")
    if not isinstance(content, list):
        raise ProviderUnavailableError("Anthropic returned an unexpected response.")
    parts: list[str] = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
            parts.append(item["text"])
    text = "".join(parts).strip()
    if not text:
        raise ProviderUnavailableError("Anthropic returned an empty response.")
    return text


def _extract_google_response(data: dict[str, Any]) -> str:
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ProviderUnavailableError("Google Gemini returned no candidates.")
    first = candidates[0]
    if not isinstance(first, dict):
        raise ProviderUnavailableError("Google Gemini returned an unexpected candidate.")
    content = first.get("content")
    if not isinstance(content, dict):
        raise ProviderUnavailableError("Google Gemini returned an unexpected content block.")
    text = _content_to_text(content.get("parts"))
    if not text:
        raise ProviderUnavailableError("Google Gemini returned an empty response.")
    return text


def _openai_compatible_url(provider: dict[str, Any]) -> str:
    provider_id = str(provider["id"])
    if provider_id == "openrouter":
        return OPENROUTER_CHAT_COMPLETIONS_URL
    if provider_id == "openai":
        return OPENAI_CHAT_COMPLETIONS_URL
    if provider_id == "groq":
        return GROQ_CHAT_COMPLETIONS_URL
    if provider_id == "minimax":
        override = os.environ.get(str(provider.get("base_url_env") or ""), "").strip()
        return override or MINIMAX_CHAT_COMPLETIONS_URL
    if provider_id == "xai":
        return XAI_CHAT_COMPLETIONS_URL
    raise ProviderNotFoundError(f"Provider {provider_id} does not use an OpenAI-compatible adapter.")


def run_provider_prompt(provider_id: str, prompt: str, model: str | None = None) -> dict[str, Any]:
    provider = _api_provider_by_id(provider_id)
    if provider is None:
        raise ProviderNotFoundError(f"Provider {provider_id} is not a configured API-key prompt provider.")
    prompt = prompt.strip()
    if not prompt:
        raise ProviderConfigError("Prompt is required.")
    if not provider_calls_enabled():
        raise ProviderConfigError("Provider prompt calls are disabled.")
    api_key = _provider_api_key(provider)
    if not api_key:
        raise ProviderConfigError(f"{provider['label']} is not configured. Set {provider['env']} before enabling provider prompt calls.")
    selected_model, request_model = _selected_provider_model(provider, model)
    adapter = str(provider["adapter"])
    label = str(provider["label"])
    if adapter in {"openrouter-chat", "openai-chat", "groq-chat", "minimax-chat", "xai-chat"}:
        payload = {
            "model": request_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        if adapter == "openrouter-chat":
            data = _post_openrouter_chat(payload, api_key)
        else:
            data = _post_provider_json(_openai_compatible_url(provider), _chat_headers(api_key), payload, label)
        response_text = _extract_chat_completion_response(data, label)
    elif adapter == "anthropic-messages":
        payload = {
            "model": request_model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        data = _post_provider_json(ANTHROPIC_MESSAGES_URL, headers, payload, label)
        response_text = _extract_anthropic_response(data)
    elif adapter == "google-generate-content":
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        url = f"{GOOGLE_GENERATE_CONTENT_URL_TEMPLATE.format(model=request_model)}?key={api_key}"
        data = _post_provider_json(url, headers, payload, label)
        response_text = _extract_google_response(data)
    else:
        raise ProviderNotFoundError(f"Provider {provider_id} does not have a prompt adapter.")
    return {
        "provider": str(provider["id"]),
        "model": selected_model,
        "request_model": request_model,
        "response": response_text,
        "usage": data.get("usage") if isinstance(data.get("usage"), dict) else data.get("usageMetadata") if isinstance(data.get("usageMetadata"), dict) else None,
    }


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
    return run_provider_prompt("openrouter", prompt, model)


def _post_openrouter_chat(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    return _post_provider_json(OPENROUTER_CHAT_COMPLETIONS_URL, _chat_headers(api_key), payload, "OpenRouter")


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
    return _extract_chat_completion_response(data, "OpenRouter")
