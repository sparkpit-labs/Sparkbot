from __future__ import annotations

import hashlib
import json
import os
import secrets
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.workstation_store import get_store


router = APIRouter()

DEFAULT_PROVIDER = "openrouter"
DEFAULT_MODEL = "openrouter/openai/gpt-4o-mini"
LOCAL_DEFAULT_MODEL = "ollama/phi4-mini"
DATA_DIR_ENV = "SPARKBOT_DATA_DIR"


PROVIDER_ENV_KEYS: dict[str, str] = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "xai": "XAI_API_KEY",
}


MODEL_LABELS: dict[str, str] = {
    DEFAULT_MODEL: "OpenRouter - GPT-4o Mini",
    "openrouter/anthropic/claude-3.5-sonnet": "OpenRouter - Claude 3.5 Sonnet",
    "openrouter/meta-llama/llama-3.1-70b-instruct:free": "OpenRouter - Llama 3.1 70B Free",
    "gpt-4o-mini": "OpenAI - GPT-4o Mini",
    "gpt-4o": "OpenAI - GPT-4o",
    "claude-3-5-sonnet-latest": "Anthropic - Claude 3.5 Sonnet",
    "gemini/gemini-2.0-flash": "Google - Gemini 2.0 Flash",
    "groq/llama-3.3-70b-versatile": "Groq - Llama 3.3 70B",
    "minimax/minimax-m2.5": "MiniMax - M2.5",
    "xai/grok-2-latest": "xAI - Grok",
    "openai-codex/gpt-5.3-codex": "OpenAI subscription - GPT coding seat",
    "claude-sub/sonnet": "Claude subscription - Sonnet",
    "ollama/llama3.2:1b": "Llama 3.2 1B - fastest local",
    "ollama/llama3.2:3b": "Llama 3.2 3B - balanced local",
    LOCAL_DEFAULT_MODEL: "Phi-4 Mini - default local",
    "ollama/mistral:7b": "Mistral 7B - stronger local",
}


PROVIDER_MODELS: dict[str, list[str]] = {
    "openrouter": [
        DEFAULT_MODEL,
        "openrouter/anthropic/claude-3.5-sonnet",
        "openrouter/meta-llama/llama-3.1-70b-instruct:free",
    ],
    "openai": ["gpt-4o-mini", "gpt-4o"],
    "anthropic": ["claude-3-5-sonnet-latest"],
    "google": ["gemini/gemini-2.0-flash"],
    "groq": ["groq/llama-3.3-70b-versatile"],
    "minimax": ["minimax/minimax-m2.5"],
    "xai": ["xai/grok-2-latest"],
    "openai_codex": ["openai-codex/gpt-5.3-codex"],
    "claude_sub": ["claude-sub/sonnet"],
    "ollama": ["ollama/llama3.2:1b", "ollama/llama3.2:3b", LOCAL_DEFAULT_MODEL, "ollama/mistral:7b"],
}


PROVIDERS: list[dict[str, Any]] = [
    {"id": "openrouter", "label": "OpenRouter", "env": "OPENROUTER_API_KEY", "auth_modes": ["api_key"]},
    {"id": "openai", "label": "OpenAI", "env": "OPENAI_API_KEY", "auth_modes": ["api_key"]},
    {"id": "anthropic", "label": "Anthropic", "env": "ANTHROPIC_API_KEY", "auth_modes": ["api_key"]},
    {"id": "google", "label": "Google", "env": "GOOGLE_API_KEY", "auth_modes": ["api_key"]},
    {"id": "groq", "label": "Groq", "env": "GROQ_API_KEY", "auth_modes": ["api_key"]},
    {"id": "minimax", "label": "MiniMax", "env": "MINIMAX_API_KEY", "auth_modes": ["api_key"]},
    {"id": "xai", "label": "xAI", "env": "XAI_API_KEY", "auth_modes": ["api_key"]},
    {"id": "openai_codex", "label": "OpenAI subscription", "env": "", "auth_modes": ["subscription"]},
    {"id": "claude_sub", "label": "Claude subscription", "env": "", "auth_modes": ["subscription"]},
    {"id": "ollama", "label": "Local Ollama", "env": "", "auth_modes": ["local"]},
]


DEFAULT_AGENTS = [
    {
        "name": "meetings_manager",
        "label": "Meetings Manager",
        "description": "Runs agendas, assignments, summaries, and follow-up plans.",
    },
    {"name": "researcher", "label": "Researcher", "description": "Investigates facts and context."},
    {"name": "analyst", "label": "Analyst", "description": "Structures tradeoffs and data."},
    {"name": "writer", "label": "Writer", "description": "Drafts notes, summaries, and messaging."},
    {"name": "builder", "label": "Builder", "description": "Turns decisions into implementation steps."},
]


class ProviderSecretsInput(BaseModel):
    openrouter_api_key: str | None = Field(default=None, max_length=4096)
    openai_api_key: str | None = Field(default=None, max_length=4096)
    anthropic_api_key: str | None = Field(default=None, max_length=4096)
    google_api_key: str | None = Field(default=None, max_length=4096)
    groq_api_key: str | None = Field(default=None, max_length=4096)
    minimax_api_key: str | None = Field(default=None, max_length=4096)
    xai_api_key: str | None = Field(default=None, max_length=4096)
    ollama_base_url: str | None = Field(default=None, max_length=300)


class LocalRuntimeInput(BaseModel):
    base_url: str | None = Field(default=None, max_length=300)
    default_local_model: str | None = Field(default=None, max_length=200)


class RoutingPolicyInput(BaseModel):
    cross_provider_fallback: bool | None = None


class ControlsConfigUpdate(BaseModel):
    default_selection: dict[str, str] | None = None
    stack: dict[str, str] | None = None
    local_runtime: LocalRuntimeInput | None = None
    routing_policy: RoutingPolicyInput | None = None
    agent_overrides: dict[str, dict[str, str]] | None = None
    providers: ProviderSecretsInput | None = None
    token_guardian_mode: str | None = Field(default=None, pattern="^(off|shadow|live)$")
    security_guardrails_enabled: bool | None = None
    custom_guardrails: str | None = Field(default=None, max_length=4000)


class ModelSelectionInput(BaseModel):
    model: str = Field(min_length=1, max_length=200)


class OperatorPinInput(BaseModel):
    current_pin: str | None = Field(default=None, max_length=64)
    pin: str = Field(min_length=6, max_length=64)


class AgentCreateInput(BaseModel):
    name: str = Field(min_length=2, max_length=64)
    description: str = Field(default="", max_length=300)
    system_prompt: str = Field(default="", max_length=4000)


class AgentUpdateInput(BaseModel):
    description: str | None = Field(default=None, max_length=300)
    system_prompt: str | None = Field(default=None, max_length=4000)


class AgentInviteRouteInput(BaseModel):
    model: str | None = Field(default=None, max_length=200)
    api_key: str | None = Field(default=None, max_length=4096)
    auth_mode: str | None = Field(default=None, max_length=40)


def _data_dir() -> Path:
    configured = os.getenv(DATA_DIR_ENV)
    base = Path(configured) if configured else Path("data") / "command-center"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _config_path() -> Path:
    return _data_dir() / "config.json"


def _secrets_path() -> Path:
    return _data_dir() / "secrets.json"


def _pin_path() -> Path:
    return _data_dir() / "operator_pin.json"


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return dict(default)
    except json.JSONDecodeError:
        return dict(default)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _default_config() -> dict[str, Any]:
    return {
        "default_selection": {"provider": DEFAULT_PROVIDER, "model": DEFAULT_MODEL},
        "stack": {
            "primary": DEFAULT_MODEL,
            "backup_1": "gpt-4o-mini",
            "backup_2": "claude-3-5-sonnet-latest",
            "heavy_hitter": "gpt-4o",
        },
        "local_runtime": {"base_url": "http://127.0.0.1:11434", "default_local_model": LOCAL_DEFAULT_MODEL},
        "routing_policy": {"cross_provider_fallback": False},
        "agent_overrides": {},
        "invite_routes": {},
        "custom_agents": [],
        "token_guardian_mode": "shadow",
        "security_guardrails_enabled": False,
        "custom_guardrails": "",
        "notices": [],
    }


def _read_config() -> dict[str, Any]:
    config = _default_config()
    stored = _read_json(_config_path(), {})
    for key, value in stored.items():
        if isinstance(value, dict) and isinstance(config.get(key), dict):
            config[key].update(value)
        else:
            config[key] = value
    return config


def _write_config(config: dict[str, Any]) -> None:
    _write_json(_config_path(), config)


def _read_secrets() -> dict[str, str]:
    return {key: str(value) for key, value in _read_json(_secrets_path(), {}).items() if value}


def _write_secrets(payload: dict[str, str]) -> None:
    _write_json(_secrets_path(), payload)


SENSITIVE_TEXT_KEYS = ("api_key", "access_key", "credential", "password", "secret", "token")
INVITE_ROUTE_AUTH_MODES = {"api_key", "oauth"}


def _slug_agent_name(value: str) -> str:
    return "".join(ch for ch in value.lower().replace(" ", "_") if ch.isalnum() or ch == "_").strip("_")


def _invite_secret_key(agent_name: str) -> str:
    return f"invite_route:{agent_name}"


def _redact_sensitive_text(value: str) -> str:
    words = value.split()
    redacted: list[str] = []
    redact_next = False
    for word in words:
        lowered = word.lower()
        key_like = any(key in lowered for key in SENSITIVE_TEXT_KEYS)
        if redact_next:
            redacted.append("[redacted]")
            redact_next = False
            continue
        if key_like and ("=" in word or ":" in word):
            separator = "=" if "=" in word else ":"
            key, _sep, maybe_value = word.partition(separator)
            redacted.append(f"{key}{separator}[redacted]" if maybe_value else word)
        else:
            redacted.append(word)
            redact_next = key_like
    return " ".join(redacted)


def _agent_record(name: str, description: str = "", system_prompt: str = "") -> dict[str, str]:
    label = name.strip()
    slug = _slug_agent_name(label)
    return {
        "name": slug,
        "label": label,
        "description": _redact_sensitive_text(description.strip()),
        "system_prompt": _redact_sensitive_text(system_prompt.strip()),
    }


def _custom_agent_records(config: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for agent in config.get("custom_agents") or []:
        if not isinstance(agent, dict):
            continue
        name = str(agent.get("name") or "").strip()
        if not name:
            continue
        records.append(
            {
                "name": name,
                "label": str(agent.get("label") or name),
                "description": str(agent.get("description") or ""),
                "system_prompt": str(agent.get("system_prompt") or ""),
            }
        )
    return records


def _agent_exists(config: dict[str, Any], slug: str) -> bool:
    return any(agent.get("name") == slug for agent in DEFAULT_AGENTS + _custom_agent_records(config))


def _normalize_auth_mode(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in INVITE_ROUTE_AUTH_MODES else "api_key"


def _invite_route_records(config: dict[str, Any], secrets_payload: dict[str, str], *, include_secret: bool = False) -> dict[str, dict[str, Any]]:
    raw_routes = config.get("invite_routes") if isinstance(config.get("invite_routes"), dict) else {}
    records: dict[str, dict[str, Any]] = {}
    for agent_name, route in raw_routes.items():
        if not isinstance(route, dict):
            continue
        slug = _slug_agent_name(str(agent_name or ""))
        if not slug:
            continue
        model = str(route.get("model") or "").strip()
        provider = str(route.get("route") or _provider_for_model(model) or "default").strip()
        if provider == "local":
            provider = "ollama"
        auth_mode = _normalize_auth_mode(str(route.get("auth_mode") or ""))
        secret_value = secrets_payload.get(_invite_secret_key(slug), "")
        record: dict[str, Any] = {
            "route": provider,
            "model": model,
            "auth_mode": auth_mode,
            "credential_configured": bool(secret_value),
        }
        if include_secret and secret_value:
            record["api_key"] = secret_value
        records[slug] = record
    return records


def _attach_invite_routes_to_agents(agents: list[dict[str, Any]], invite_routes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for agent in agents:
        row = dict(agent)
        route = invite_routes.get(str(agent.get("name") or ""))
        if route:
            row["invite_route"] = {key: value for key, value in route.items() if key != "api_key"}
        rows.append(row)
    return rows


def _provider_for_model(model: str) -> str:
    normalized = (model or "").strip()
    if normalized.startswith("openrouter/"):
        return "openrouter"
    if normalized.startswith("ollama/"):
        return "ollama"
    if normalized.startswith("openai-codex/"):
        return "openai_codex"
    if normalized.startswith("claude-sub/"):
        return "claude_sub"
    if normalized.startswith("gemini/"):
        return "google"
    if normalized.startswith("groq/"):
        return "groq"
    if normalized.startswith("minimax/"):
        return "minimax"
    if normalized.startswith("xai/"):
        return "xai"
    if normalized.startswith("claude-"):
        return "anthropic"
    if normalized.startswith("gpt-"):
        return "openai"
    return ""


def _valid_model(model: str) -> bool:
    normalized = (model or "").strip()
    if normalized in MODEL_LABELS:
        return True
    return normalized.startswith("openrouter/") or normalized.startswith("ollama/")


def _configured_provider(provider_id: str, secrets_payload: dict[str, str]) -> bool:
    if provider_id == "ollama":
        return True
    if provider_id in {"openai_codex", "claude_sub"}:
        return False
    env_key = PROVIDER_ENV_KEYS.get(provider_id, "")
    return bool((env_key and os.getenv(env_key, "").strip()) or secrets_payload.get(provider_id))


async def _ollama_status(base_url: str | None = None) -> dict[str, Any]:
    endpoint_base = (base_url or "http://127.0.0.1:11434").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{endpoint_base}/api/tags")
            response.raise_for_status()
        payload = response.json()
        model_names = [
            str(item.get("name") or "").strip()
            for item in payload.get("models", [])
            if str(item.get("name") or "").strip()
        ]
        model_ids = [name if name.startswith("ollama/") else f"ollama/{name}" for name in model_names]
        return {
            "base_url": endpoint_base,
            "reachable": True,
            "models_available": bool(model_ids),
            "models": model_ids,
            "model_ids": model_ids,
            "error": None,
        }
    except Exception as exc:
        return {
            "base_url": endpoint_base,
            "reachable": False,
            "models_available": False,
            "models": [],
            "model_ids": [],
            "error": f"Local model service is unavailable: {exc}",
        }


def _pin_configured() -> bool:
    return _pin_path().exists()


def _verify_pin(pin: str | None) -> bool:
    if not pin:
        return False
    stored = _read_json(_pin_path(), {})
    salt = str(stored.get("salt") or "")
    expected = str(stored.get("hash") or "")
    if not salt or not expected:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), bytes.fromhex(salt), 120_000).hex()
    return secrets.compare_digest(digest, expected)


def _set_pin(pin: str) -> None:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 120_000).hex()
    _write_json(_pin_path(), {"salt": salt.hex(), "hash": digest})


def _provider_catalog(config: dict[str, Any], secrets_payload: dict[str, str], ollama_status: dict[str, Any]) -> list[dict[str, Any]]:
    providers: list[dict[str, Any]] = []
    for item in PROVIDERS:
        provider_id = str(item["id"])
        row = {
            "id": provider_id,
            "label": item["label"],
            "configured": _configured_provider(provider_id, secrets_payload),
            "auth_modes": item["auth_modes"],
            "models": PROVIDER_MODELS.get(provider_id, []),
            "models_available": bool(PROVIDER_MODELS.get(provider_id)),
            "available_models": PROVIDER_MODELS.get(provider_id, []),
        }
        if provider_id == "ollama":
            row.update(
                {
                    "configured": True,
                    "reachable": bool(ollama_status.get("reachable")),
                    "models_available": bool(ollama_status.get("models_available")),
                    "available_models": list(ollama_status.get("model_ids") or []),
                    "models": list(ollama_status.get("model_ids") or PROVIDER_MODELS["ollama"]),
                    "base_url": config["local_runtime"]["base_url"],
                }
            )
        providers.append(row)
    return providers


async def _build_controls_config(notices: list[str] | None = None) -> dict[str, Any]:
    config = _read_config()
    secrets_payload = _read_secrets()
    ollama = await _ollama_status(config["local_runtime"].get("base_url"))
    invite_routes = _invite_route_records(config, secrets_payload)
    agents = _attach_invite_routes_to_agents(DEFAULT_AGENTS + _custom_agent_records(config), invite_routes)
    default_model = str(config["default_selection"].get("model") or DEFAULT_MODEL)
    return {
        "active_model": default_model,
        "default_selection": {
            "provider": config["default_selection"].get("provider") or _provider_for_model(default_model) or DEFAULT_PROVIDER,
            "model": default_model,
            "label": MODEL_LABELS.get(default_model, default_model),
        },
        "stack": config["stack"],
        "local_runtime": config["local_runtime"],
        "routing_policy": config["routing_policy"],
        "agent_overrides": config.get("agent_overrides") or {},
        "available_agents": agents,
        "model_labels": MODEL_LABELS,
        "providers": _provider_catalog(config, secrets_payload, ollama),
        "ollama_status": ollama,
        "token_guardian_mode": config.get("token_guardian_mode", "shadow"),
        "security_guardrails_enabled": bool(config.get("security_guardrails_enabled")),
        "custom_guardrails": str(config.get("custom_guardrails") or ""),
        "pin_configured": _pin_configured(),
        "notices": notices or [],
    }


@router.get("/api/v1/chat/models/config")
async def get_models_config() -> dict[str, Any]:
    return await _build_controls_config()


@router.post("/api/v1/chat/models/config")
async def update_models_config(body: ControlsConfigUpdate) -> dict[str, Any]:
    config = _read_config()
    secrets_payload = _read_secrets()
    notices: list[str] = []

    if body.default_selection is not None:
        provider = str(body.default_selection.get("provider") or "").strip()
        model = str(body.default_selection.get("model") or "").strip()
        if provider not in {item["id"] for item in PROVIDERS}:
            raise HTTPException(status_code=400, detail="Unknown provider.")
        if not _valid_model(model):
            raise HTTPException(status_code=400, detail="Unknown model.")
        actual_provider = _provider_for_model(model)
        if provider != actual_provider:
            raise HTTPException(status_code=400, detail="Model does not match the selected provider.")
        config["default_selection"] = {"provider": provider, "model": model}
        config["stack"]["primary"] = model
        if provider == "ollama":
            config["local_runtime"]["default_local_model"] = model
        notices.append("Default model saved.")

    if body.stack is not None:
        next_stack = dict(config["stack"])
        for key in ("primary", "backup_1", "backup_2", "heavy_hitter"):
            value = str(body.stack.get(key) or "").strip()
            if value:
                if not _valid_model(value):
                    raise HTTPException(status_code=400, detail=f"Unknown model for {key}.")
                next_stack[key] = value
        config["stack"] = next_stack
        notices.append("Model stack saved.")

    if body.local_runtime is not None:
        if body.local_runtime.base_url:
            config["local_runtime"]["base_url"] = body.local_runtime.base_url.strip().rstrip("/")
            notices.append("Local model endpoint saved.")
        if body.local_runtime.default_local_model:
            local_model = body.local_runtime.default_local_model.strip()
            if _provider_for_model(local_model) != "ollama":
                raise HTTPException(status_code=400, detail="Local default model must be an Ollama model.")
            config["local_runtime"]["default_local_model"] = local_model
            notices.append("Preferred local model saved.")

    if body.routing_policy is not None and body.routing_policy.cross_provider_fallback is not None:
        config["routing_policy"]["cross_provider_fallback"] = bool(body.routing_policy.cross_provider_fallback)
        notices.append("Routing policy saved.")

    if body.agent_overrides is not None:
        cleaned: dict[str, dict[str, str]] = {}
        allowed_routes = {item["id"] for item in PROVIDERS} | {"default", "local"}
        for agent, override in body.agent_overrides.items():
            route = str((override or {}).get("route") or "default").strip()
            model = str((override or {}).get("model") or "").strip()
            if route not in allowed_routes:
                raise HTTPException(status_code=400, detail=f"Invalid route for {agent}.")
            if route == "local":
                route = "ollama"
            if model and not _valid_model(model):
                raise HTTPException(status_code=400, detail=f"Unknown model for {agent}.")
            if route not in {"default"} and model and _provider_for_model(model) != route:
                raise HTTPException(status_code=400, detail=f"Model route mismatch for {agent}.")
            cleaned[agent.strip().lower()] = {"route": route, "model": model}
        config["agent_overrides"] = cleaned
        notices.append("Agent routing overrides saved.")

    if body.providers is not None:
        provider_secret_fields = {
            "openrouter": body.providers.openrouter_api_key,
            "openai": body.providers.openai_api_key,
            "anthropic": body.providers.anthropic_api_key,
            "google": body.providers.google_api_key,
            "groq": body.providers.groq_api_key,
            "minimax": body.providers.minimax_api_key,
            "xai": body.providers.xai_api_key,
        }
        for provider_id, value in provider_secret_fields.items():
            if value and value.strip():
                secrets_payload[provider_id] = value.strip()
                notices.append(f"{provider_id} credential saved server-side.")
        if body.providers.ollama_base_url:
            config["local_runtime"]["base_url"] = body.providers.ollama_base_url.strip().rstrip("/")
            notices.append("Local model endpoint saved.")

    if body.token_guardian_mode is not None:
        config["token_guardian_mode"] = body.token_guardian_mode
        notices.append("Model routing monitor mode saved.")

    if body.security_guardrails_enabled is not None:
        config["security_guardrails_enabled"] = bool(body.security_guardrails_enabled)
        notices.append("Security profile saved.")

    if body.custom_guardrails is not None:
        config["custom_guardrails"] = body.custom_guardrails
        notices.append("Custom guardrails saved.")

    _write_config(config)
    if body.providers is not None:
        _write_secrets(secrets_payload)
    if notices:
        get_store().append_event({
            "event_type": "command_center.config_updated",
            "surface": "command_center",
            "summary": "Command Center configuration updated.",
            "payload": {"notices": notices},
        })
    return await _build_controls_config(notices=notices)


@router.get("/api/v1/chat/model")
async def get_model() -> dict[str, Any]:
    config = await _build_controls_config()
    return config["default_selection"]


@router.post("/api/v1/chat/model")
async def set_model(body: ModelSelectionInput) -> dict[str, Any]:
    model = body.model.strip()
    if not _valid_model(model):
        raise HTTPException(status_code=400, detail="Unknown model.")
    provider = _provider_for_model(model)
    config = _read_config()
    config["default_selection"] = {"provider": provider, "model": model}
    config["stack"]["primary"] = model
    _write_config(config)
    get_store().append_event({
        "event_type": "model.default_updated",
        "surface": "command_center",
        "summary": "Default model updated.",
        "payload": {"model": model, "provider": provider},
    })
    return {"model": model, "provider": provider, "label": MODEL_LABELS.get(model, model)}


@router.get("/api/v1/chat/ollama/status")
async def get_ollama_status() -> dict[str, Any]:
    config = _read_config()
    return await _ollama_status(config["local_runtime"].get("base_url"))


@router.get("/api/v1/chat/openrouter/models")
async def openrouter_models() -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip() or _read_secrets().get("openrouter", "")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://openrouter.ai/api/v1/models", headers=headers)
            response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not load OpenRouter models: {exc}")

    rows: list[dict[str, Any]] = []
    for item in payload.get("data", []):
        raw_id = str(item.get("id") or "").strip()
        if not raw_id:
            continue
        pricing = item.get("pricing") or {}
        is_free = raw_id.endswith(":free") or (
            str(pricing.get("prompt") or "1") == "0" and str(pricing.get("completion") or "1") == "0"
        )
        rows.append(
            {
                "id": f"openrouter/{raw_id}",
                "raw_id": raw_id,
                "label": str(item.get("name") or raw_id),
                "context_length": item.get("context_length"),
                "pricing": pricing,
                "is_free": is_free,
            }
        )
    rows.sort(key=lambda row: (not bool(row["is_free"]), str(row["label"]).lower()))
    return {"models": rows}


@router.get("/api/v1/chat/agents")
async def list_agents() -> dict[str, Any]:
    config = _read_config()
    invite_routes = _invite_route_records(config, _read_secrets())
    return {"agents": _attach_invite_routes_to_agents(DEFAULT_AGENTS + _custom_agent_records(config), invite_routes)}


@router.post("/api/v1/chat/agents", status_code=201)
async def create_agent(body: AgentCreateInput) -> dict[str, Any]:
    config = _read_config()
    agent = _agent_record(body.name, body.description, body.system_prompt)
    slug = agent["name"]
    if not slug:
        raise HTTPException(status_code=400, detail="Agent name must contain letters or numbers.")
    agents = list(config.get("custom_agents") or [])
    if any(item["name"] == slug for item in DEFAULT_AGENTS + agents):
        raise HTTPException(status_code=409, detail="Agent already exists.")
    agents.append(agent)
    config["custom_agents"] = agents
    _write_config(config)
    get_store().append_event({
        "event_type": "agent.created",
        "surface": "command_center",
        "source_id": slug,
        "summary": f"Agent created: {agent['label']}",
        "payload": {"agent": slug},
    })
    return agent


@router.patch("/api/v1/chat/agents/{agent_name}")
async def update_agent(agent_name: str, body: AgentUpdateInput) -> dict[str, Any]:
    config = _read_config()
    slug = _slug_agent_name(agent_name)
    if any(agent["name"] == slug for agent in DEFAULT_AGENTS):
        raise HTTPException(status_code=400, detail="Packaged agents cannot be edited in this public slice.")
    agents = list(config.get("custom_agents") or [])
    for index, agent in enumerate(agents):
        if agent.get("name") != slug:
            continue
        updated = dict(agent)
        if body.description is not None:
            updated["description"] = _redact_sensitive_text(body.description.strip())
        if body.system_prompt is not None:
            updated["system_prompt"] = _redact_sensitive_text(body.system_prompt.strip())
        agents[index] = updated
        config["custom_agents"] = agents
        _write_config(config)
        get_store().append_event({
            "event_type": "agent.updated",
            "surface": "command_center",
            "source_id": slug,
            "summary": f"Agent updated: {updated.get('label') or slug}",
            "payload": {"agent": slug},
        })
        return updated
    raise HTTPException(status_code=404, detail="Custom agent not found.")


@router.post("/api/v1/chat/agents/{agent_name}/invite-route")
async def set_agent_invite_route(agent_name: str, body: AgentInviteRouteInput) -> dict[str, Any]:
    config = _read_config()
    secrets_payload = _read_secrets()
    slug = _slug_agent_name(agent_name)
    if not slug or not _agent_exists(config, slug):
        raise HTTPException(status_code=404, detail="Agent not found.")

    model = (body.model or "").strip()
    api_key = (body.api_key or "").strip()
    requested_auth_mode = (body.auth_mode or "").strip().lower()
    if requested_auth_mode and requested_auth_mode not in INVITE_ROUTE_AUTH_MODES:
        raise HTTPException(status_code=400, detail="Unsupported invite route auth mode in this public slice.")
    auth_mode = _normalize_auth_mode(body.auth_mode)
    invite_routes = dict(config.get("invite_routes") or {})
    secret_key = _invite_secret_key(slug)

    if not model and not api_key:
        invite_routes.pop(slug, None)
        secrets_payload.pop(secret_key, None)
        config["invite_routes"] = invite_routes
        _write_config(config)
        _write_secrets(secrets_payload)
        get_store().append_event({
            "event_type": "agent.invite_route.cleared",
            "surface": "command_center",
            "source_id": slug,
            "summary": "Agent invite route cleared.",
            "payload": {"agent": slug},
        })
        return {"name": slug, "configured": False, "invite_route": None}

    if model and not _valid_model(model):
        raise HTTPException(status_code=400, detail="Unknown invite route model.")
    route = _provider_for_model(model) if model else "default"
    if route == "local":
        route = "ollama"
    if route in {"openai_codex", "claude_sub"}:
        raise HTTPException(status_code=400, detail="Subscription-only invite routes are not available for server-side execution in this public slice.")
    if auth_mode == "oauth" and route != "anthropic":
        raise HTTPException(status_code=400, detail="OAuth invite auth mode is only supported for Anthropic provider routes.")
    if api_key:
        secrets_payload[secret_key] = api_key
    credential_configured = bool(api_key or secrets_payload.get(secret_key))
    invite_routes[slug] = {
        "route": route or "default",
        "model": model,
        "auth_mode": auth_mode,
        "credential_configured": credential_configured,
    }
    config["invite_routes"] = invite_routes
    _write_config(config)
    if api_key:
        _write_secrets(secrets_payload)
    safe_route = _invite_route_records(config, secrets_payload).get(slug)
    get_store().append_event({
        "event_type": "agent.invite_route.updated",
        "surface": "command_center",
        "source_id": slug,
        "summary": "Agent invite route updated.",
        "payload": {"agent": slug, "route": safe_route.get("route") if safe_route else "default", "model": safe_route.get("model") if safe_route else ""},
    })
    return {"name": slug, "configured": True, "invite_route": safe_route}


@router.delete("/api/v1/chat/agents/{agent_name}/invite-route")
async def clear_agent_invite_route(agent_name: str) -> dict[str, Any]:
    return await set_agent_invite_route(agent_name, AgentInviteRouteInput())


@router.get("/api/v1/chat/guardian/status")
async def guardian_status() -> dict[str, Any]:
    config = _read_config()
    return {
        "available": True,
        "security_guardrails_enabled": bool(config.get("security_guardrails_enabled")),
        "pin_configured": _pin_configured(),
        "task_guardian_enabled": False,
        "memory_guardian_enabled": False,
        "token_guardian_mode": config.get("token_guardian_mode", "shadow"),
        "breakglass": {"active": False},
        "vault": {"configured": _secrets_path().exists(), "mode": "server-side local config"},
    }


@router.get("/api/v1/chat/security/status")
async def security_status() -> dict[str, Any]:
    config = _read_config()
    return {
        "operator": {
            "mode": "local",
            "pin_configured": _pin_configured(),
            "breakglass_active": False,
            "usernames": [],
        },
        "passphrase": {"label": "local", "configured": False},
        "security_guardrails_enabled": bool(config.get("security_guardrails_enabled")),
        "custom_guardrails": str(config.get("custom_guardrails") or ""),
        "provider_storage": "server-side only",
        "operator_guidance": [
            {"area": "providers", "operator_action": "Keep credentials in environment or local backend config."},
            {"area": "actions", "operator_action": "Unsupported action paths remain disabled until backend gates are ported."},
        ],
    }


@router.post("/api/v1/chat/security/operator-pin")
async def save_operator_pin(body: OperatorPinInput) -> dict[str, Any]:
    if _pin_configured() and not _verify_pin(body.current_pin):
        raise HTTPException(status_code=403, detail="Current PIN is required to change the PIN.")
    if not body.pin.isdigit() or len(body.pin) != 6:
        raise HTTPException(status_code=400, detail="PIN must be six digits.")
    _set_pin(body.pin)
    get_store().append_event({
        "event_type": "guardian.pin_updated",
        "surface": "guardian",
        "summary": "Operator PIN updated.",
        "payload": {"pin_configured": True},
    })
    return {"ok": True, "pin_configured": True}


@router.get("/api/v1/chat/dashboard/summary")
async def dashboard_summary() -> dict[str, Any]:
    config = _read_config()
    store_summary = get_store().dashboard_summary()
    return {
        "summary": {
            "rooms_count": store_summary["rooms_count"],
            "open_tasks": 0,
            "pending_reminders": 0,
            "pending_approvals": store_summary["pending_confirmations"],
            "guardian_jobs": store_summary["notes_count"],
            "guardian_jobs_enabled": 0,
            "task_guardian_enabled": False,
            "token_guardian_mode": config.get("token_guardian_mode", "shadow"),
            "security_guardrails_enabled": bool(config.get("security_guardrails_enabled")),
            "notes_count": store_summary["notes_count"],
            "memory_count": store_summary["memory_count"],
            "events_count": store_summary["events_count"],
            "seat_count": store_summary["seat_count"],
        },
        "today": {"meeting_artifacts": [], "inbox": {"summary_text": "Connectors are not configured in this public port."}},
    }


@router.get("/api/v1/chat/spine/operator/overview")
async def spine_overview() -> dict[str, Any]:
    empty: list[Any] = []
    store_summary = get_store().dashboard_summary()
    return {
        "open_queue": empty,
        "blocked_queue": empty,
        "approval_waiting_queue": empty,
        "stale_queue": empty,
        "orphan_queue": empty,
        "missing_source_queue": empty,
        "missing_project_queue": empty,
        "recently_resurfaced_queue": empty,
        "assignment_ready_queue": empty,
        "executive_directives_queue": empty,
        "status": "available",
        "note": "Spine inspection route is backed by shared Workstation state; full task queues are a follow-up port.",
        "workstation_counts": store_summary,
    }


@router.get("/api/v1/chat/spine/operator/events")
async def spine_events() -> dict[str, Any]:
    events = get_store().list_events(limit=100)
    return {"events": events, "count": len(events)}


@router.get("/api/v1/chat/spine/operator/producers")
async def spine_producers() -> dict[str, Any]:
    producers = [
        {"subsystem": "workstation", "description": "Shared local Workstation state", "event_types": ["room.created", "note.saved", "memory.saved", "seat.updated"]},
        {"subsystem": "command_center", "description": "Command Center configuration changes", "event_types": ["command_center.config_updated", "model.default_updated", "agent.created"]},
    ]
    return {"producers": producers, "count": len(producers)}


@router.get("/api/v1/chat/spine/operator/projects")
async def spine_projects() -> dict[str, Any]:
    rooms = get_store().list_rooms(limit=100)
    projects = [
        {
            "project_id": room["id"],
            "display_name": room["title"],
            "status": room["status"],
            "summary": room["summary"],
            "updated_at": room["updated_at"],
        }
        for room in rooms
    ]
    return {"projects": projects, "count": len(projects)}


@router.get("/api/v1/utils/health-check/")
async def api_health_check() -> bool:
    return True
