from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib import error, parse, request

DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
LOCAL_MODEL_ENABLE_VALUES = {"1", "true", "yes"}
MODEL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,119}$")
PROMPT_TIMEOUT_SECONDS = 20
STATUS_TIMEOUT_SECONDS = 2


class LocalModelAdapterError(RuntimeError):
    pass


class LocalModelConfigError(LocalModelAdapterError):
    pass


class LocalModelUnavailableError(LocalModelAdapterError):
    pass


def local_models_enabled() -> bool:
    return os.environ.get("SPARKBOT_LOCAL_MODELS_ENABLED", "").strip().lower() in LOCAL_MODEL_ENABLE_VALUES


def validate_local_ollama_url(url: str) -> str:
    parsed = parse.urlparse(url.strip())
    if parsed.scheme != "http":
        raise LocalModelConfigError("Ollama base URL must use http on localhost.")
    if parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise LocalModelConfigError("Ollama base URL must use localhost or 127.0.0.1.")
    if parsed.username or parsed.password:
        raise LocalModelConfigError("Ollama base URL must not include credentials.")
    if parsed.params or parsed.query or parsed.fragment:
        raise LocalModelConfigError("Ollama base URL must not include parameters, query, or fragment.")
    if parsed.path not in {"", "/"}:
        raise LocalModelConfigError("Ollama base URL must point to the local server root.")
    return parse.urlunparse((parsed.scheme, parsed.netloc, "", "", "", "")).rstrip("/")


def get_ollama_base_url() -> str:
    return validate_local_ollama_url(os.environ.get("SPARKBOT_OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL))


def validate_model_name(model: str) -> str:
    model = model.strip()
    if not MODEL_NAME_PATTERN.fullmatch(model):
        raise LocalModelConfigError("Ollama model name must be a safe local model identifier.")
    return model


def get_configured_model() -> str | None:
    configured = os.environ.get("SPARKBOT_OLLAMA_MODEL", "").strip()
    if not configured:
        return None
    return validate_model_name(configured)


def get_ollama_status() -> dict[str, Any]:
    enabled = local_models_enabled()
    try:
        base_url = get_ollama_base_url()
        configured_model = get_configured_model()
    except LocalModelConfigError as exc:
        return {
            "service": "sparkbot-server",
            "mode": "local",
            "status": "unavailable",
            "local_models_enabled": enabled,
            "adapter": "ollama",
            "base_url": None,
            "base_url_policy": "localhost-only",
            "configured_model": None,
            "prompt_calls": "disabled" if not enabled else "unavailable",
            "credentials": "not-supported",
            "external_network": "not-supported",
            "configuration_error": str(exc),
        }

    response: dict[str, Any] = {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "disabled-by-default" if not enabled else "unavailable",
        "local_models_enabled": enabled,
        "adapter": "ollama",
        "base_url": base_url,
        "base_url_policy": "localhost-only",
        "configured_model": configured_model,
        "prompt_calls": "disabled" if not enabled else "enabled-local-only",
        "credentials": "not-supported",
        "external_network": "not-supported",
    }
    if not enabled:
        return response

    try:
        _request_json(f"{base_url}/api/tags", timeout=STATUS_TIMEOUT_SECONDS)
    except LocalModelUnavailableError:
        return {**response, "ollama_reachable": False}
    return {**response, "status": "available-local-only", "ollama_reachable": True}


def run_ollama_prompt(prompt: str, model: str | None = None) -> dict[str, Any]:
    prompt = prompt.strip()
    if not prompt:
        raise LocalModelConfigError("Prompt is required.")
    selected_model = validate_model_name(model) if model else get_configured_model()
    if not selected_model:
        raise LocalModelConfigError("A local Ollama model must be configured or provided.")
    base_url = get_ollama_base_url()
    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
    }
    data = _request_json(f"{base_url}/api/generate", payload=payload, timeout=PROMPT_TIMEOUT_SECONDS)
    response_text = str(data.get("response", "")).strip()
    if not response_text:
        raise LocalModelUnavailableError("Ollama returned an empty response.")
    return {
        "adapter": "ollama",
        "base_url_policy": "localhost-only",
        "model": selected_model,
        "response": response_text,
        "done": bool(data.get("done", True)),
    }


def _request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = STATUS_TIMEOUT_SECONDS) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, headers=headers, method="GET" if body is None else "POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except (error.URLError, TimeoutError, OSError) as exc:
        raise LocalModelUnavailableError("Local Ollama endpoint is unavailable.") from exc
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise LocalModelUnavailableError("Local Ollama endpoint returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise LocalModelUnavailableError("Local Ollama endpoint returned an unexpected response.")
    return parsed
