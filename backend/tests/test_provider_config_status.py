from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app
from app.services import provider_runtime


def _provider_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {provider["id"]: provider for provider in payload["providers"]}


def _walk_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        keys = list(value.keys())
        for child in value.values():
            keys.extend(_walk_keys(child))
        return keys
    if isinstance(value, list):
        keys: list[str] = []
        for child in value:
            keys.extend(_walk_keys(child))
        return keys
    return []


def test_provider_config_status_exposes_env_and_cli_onboarding(monkeypatch) -> None:
    monkeypatch.delenv("SPARKBOT_PROVIDER_CALLS_ENABLED", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("SPARKBOT_LOCAL_MODELS_ENABLED", raising=False)
    client = TestClient(app)
    response = client.get("/provider-config/status")

    assert response.status_code == 200
    payload = response.json()
    providers = _provider_by_id(payload)

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "disabled-by-default"
    assert payload["credential_storage"] == "not-implemented"
    assert payload["provider_calls"] == "disabled-by-default"
    assert payload["model_routing"] == "env-driven"
    assert set(providers) == {
        "local-ollama",
        "openrouter",
        "openai",
        "anthropic",
        "google",
        "groq",
        "minimax",
        "xai",
        "openai-codex-subscription",
        "claude-subscription",
    }
    assert providers["openrouter"]["credential_source"] == "OPENROUTER_API_KEY"
    assert providers["openrouter"]["default_model"].endswith(":free")
    assert providers["openrouter"]["configured"] is False
    assert providers["openrouter"]["status"] == "planned"
    codex = providers["openai-codex-subscription"]
    claude = providers["claude-subscription"]
    assert codex["auth_mode"] == "codex-cli-sign-in"
    assert codex["runtime_gate"] == "lima-guardian-required"
    assert isinstance(codex["cli_available"], bool)
    assert isinstance(codex["sign_in_detected"], bool)
    assert codex["operator_action"]
    assert claude["auth_mode"] == "claude-cli-sign-in"
    assert claude["runtime_gate"] == "lima-guardian-required"
    assert isinstance(claude["cli_available"], bool)
    assert isinstance(claude["sign_in_detected"], bool)
    assert claude["operator_action"]


def test_subscription_provider_readiness_tracks_cli_and_sign_in(monkeypatch) -> None:
    monkeypatch.setattr(provider_runtime, "_codex_cli_available", lambda: True)
    monkeypatch.setattr(provider_runtime, "_codex_auth_file_exists", lambda: True)
    monkeypatch.setattr(provider_runtime, "_claude_cli_available", lambda: True)
    monkeypatch.setattr(provider_runtime, "_claude_subscription_hint_present", lambda: True)

    payload = provider_runtime.get_provider_config_status()
    providers = _provider_by_id(payload)

    codex = providers["openai-codex-subscription"]
    claude = providers["claude-subscription"]
    assert codex["configured"] is True
    assert codex["status"] == "disabled-by-default"
    assert codex["cli_available"] is True
    assert codex["sign_in_detected"] is True
    assert "LIMA Guardian" in codex["operator_action"]
    assert claude["configured"] is True
    assert claude["status"] == "disabled-by-default"
    assert claude["cli_available"] is True
    assert claude["sign_in_detected"] is True
    assert "LIMA Guardian" in claude["operator_action"]


def test_subscription_provider_requires_cli_and_sign_in(monkeypatch) -> None:
    monkeypatch.setattr(provider_runtime, "_codex_cli_available", lambda: False)
    monkeypatch.setattr(provider_runtime, "_codex_auth_file_exists", lambda: True)
    monkeypatch.setattr(provider_runtime, "_claude_cli_available", lambda: True)
    monkeypatch.setattr(provider_runtime, "_claude_subscription_hint_present", lambda: False)

    payload = provider_runtime.get_provider_config_status()
    providers = _provider_by_id(payload)

    codex = providers["openai-codex-subscription"]
    claude = providers["claude-subscription"]
    assert codex["configured"] is False
    assert codex["status"] == "planned"
    assert codex["cli_available"] is False
    assert codex["sign_in_detected"] is True
    assert "Install the Codex CLI" in codex["operator_action"]
    assert claude["configured"] is False
    assert claude["status"] == "planned"
    assert claude["cli_available"] is True
    assert claude["sign_in_detected"] is False
    assert "Sign in with Claude Code" in claude["operator_action"]


def test_subscription_provider_detects_portable_cli_and_auth_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex-profile"))
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "claude-profile"))
    monkeypatch.delenv("SPARKBOT_CODEX_CLI", raising=False)
    monkeypatch.delenv("SPARKBOT_CLAUDE_CLI", raising=False)
    monkeypatch.delenv("SPARKBOT_CLAUDE_AUTH_FILE", raising=False)
    monkeypatch.setattr(provider_runtime.shutil, "which", lambda executable: None)

    codex_auth = tmp_path / "codex-profile" / "auth.json"
    codex_auth.parent.mkdir()
    codex_auth.write_text("{}")
    claude_home = tmp_path / "claude-profile"
    claude_home.mkdir()
    local_bin = tmp_path / ".local" / "bin"
    local_bin.mkdir(parents=True)
    (local_bin / "codex").write_text("")
    (local_bin / "claude").write_text("")

    assert provider_runtime._codex_cli_available() is True
    assert provider_runtime._codex_auth_file_exists() is True
    assert provider_runtime._claude_cli_available() is True
    assert provider_runtime._claude_subscription_hint_present() is True


def test_subscription_provider_supports_auth_file_and_model_alias_envs(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SPARKBOT_CODEX_SUBSCRIPTION_MODEL", "openai-codex/gpt-5.4")
    monkeypatch.delenv("SPARKBOT_CODEX_MODEL", raising=False)
    monkeypatch.setenv("SPARKBOT_CLAUDE_SUBSCRIPTION_MODEL", "claude-sub/opus")
    monkeypatch.delenv("SPARKBOT_CLAUDE_SUB_MODEL", raising=False)
    monkeypatch.setattr(provider_runtime, "_codex_cli_available", lambda: True)
    monkeypatch.setattr(provider_runtime, "_codex_auth_file_exists", lambda: True)
    monkeypatch.setattr(provider_runtime, "_claude_cli_available", lambda: True)
    claude_auth = tmp_path / "claude-auth.json"
    claude_auth.write_text("{}")
    monkeypatch.setenv("SPARKBOT_CLAUDE_AUTH_FILE", str(claude_auth))
    monkeypatch.delenv("SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED", raising=False)

    payload = provider_runtime.get_provider_config_status()
    providers = _provider_by_id(payload)

    assert providers["openai-codex-subscription"]["default_model"] == "openai-codex/gpt-5.4"
    assert providers["openai-codex-subscription"]["credential_source"] == "CODEX_HOME or SPARKBOT_CODEX_AUTH_FILE"
    assert providers["claude-subscription"]["default_model"] == "claude-sub/opus"
    assert providers["claude-subscription"]["credential_source"] == "CLAUDE_HOME or SPARKBOT_CLAUDE_AUTH_FILE"
    assert providers["claude-subscription"]["sign_in_detected"] is True


def test_provider_statuses_use_contract_values_and_reflect_enabled_api_providers(monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("MINIMAX_API_KEY", "test-minimax-key")
    monkeypatch.setenv("XAI_API_KEY", "test-xai-key")
    monkeypatch.setenv("SPARKBOT_OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")

    client = TestClient(app)
    payload = client.get("/provider-config/status").json()
    providers = _provider_by_id(payload)

    assert {provider["status"] for provider in payload["providers"]} <= ALLOWED_CAPABILITY_STATUSES
    assert payload["status"] == "available"
    assert payload["provider_calls"] == "guarded-manual"
    for provider_id in ("openrouter", "openai", "anthropic", "google", "groq", "minimax", "xai"):
        assert providers[provider_id]["status"] == "available"
        assert providers[provider_id]["configured"] is True
        assert providers[provider_id]["prompt_endpoint"] == f"/provider-config/{provider_id}/prompt"
        assert providers[provider_id]["prompt_adapter"]
    assert providers["openrouter"]["default_model"] == "mistralai/mistral-7b-instruct:free"


def test_provider_config_status_contains_no_secret_value_fields(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "super-sensitive-test-value")
    client = TestClient(app)
    payload = client.get("/provider-config/status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)

    serialized = str(payload)
    assert "super-sensitive-test-value" not in serialized
    assert "Bearer" not in serialized


def test_openrouter_prompt_endpoint_returns_403_when_disabled(monkeypatch) -> None:
    monkeypatch.delenv("SPARKBOT_PROVIDER_CALLS_ENABLED", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    client = TestClient(app)

    response = client.post(
        "/provider-config/openrouter/prompt",
        json={"prompt": "Say OK.", "model": "mistralai/mistral-7b-instruct:free"},
    )

    assert response.status_code == 403


def test_api_provider_prompt_endpoint_returns_403_when_disabled(monkeypatch) -> None:
    monkeypatch.delenv("SPARKBOT_PROVIDER_CALLS_ENABLED", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    client = TestClient(app)

    response = client.post(
        "/provider-config/openai/prompt",
        json={"prompt": "Say OK.", "model": "gpt-5-mini"},
    )

    assert response.status_code == 403


def test_subscription_prompt_routes_remain_missing_even_when_disabled(monkeypatch) -> None:
    monkeypatch.delenv("SPARKBOT_PROVIDER_CALLS_ENABLED", raising=False)
    client = TestClient(app)

    assert client.post("/provider-config/openai-codex-subscription/prompt", json={"prompt": "x"}).status_code == 404
    assert client.post("/provider-config/claude-subscription/prompt", json={"prompt": "x"}).status_code == 404


def test_provider_prompt_requires_configured_key(monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(app)

    response = client.post(
        "/provider-config/openai/prompt",
        json={"prompt": "Say OK.", "model": "gpt-5-mini"},
    )

    assert response.status_code == 400
    assert "not configured" in response.json()["detail"]


def test_openrouter_prompt_enforces_free_models_by_default(monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.delenv("SPARKBOT_ALLOW_PAID_OPENROUTER_MODELS", raising=False)
    client = TestClient(app)

    response = client.post(
        "/provider-config/openrouter/prompt",
        json={"prompt": "Say OK.", "model": "openrouter/openai/gpt-4o-mini"},
    )

    assert response.status_code == 400
    assert ":free" in response.json()["detail"]


def test_mocked_openrouter_prompt_success(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_post(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
        captured["payload"] = payload
        captured["api_key"] = api_key
        return {
            "choices": [{"message": {"content": "OK from OpenRouter"}}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 3},
        }

    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setattr(provider_runtime, "_post_openrouter_chat", fake_post)
    client = TestClient(app)

    response = client.post(
        "/provider-config/openrouter/prompt",
        json={"prompt": "Say OK.", "model": "openrouter/mistralai/mistral-7b-instruct:free"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "provider": "openrouter",
        "model": "openrouter/mistralai/mistral-7b-instruct:free",
        "request_model": "mistralai/mistral-7b-instruct:free",
        "response": "OK from OpenRouter",
        "usage": {"prompt_tokens": 4, "completion_tokens": 3},
    }
    assert captured["payload"]["model"] == "mistralai/mistral-7b-instruct:free"
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["messages"] == [{"role": "user", "content": "Say OK."}]
    assert captured["api_key"] == "test-openrouter-key"


def test_openrouter_provider_failure_returns_safe_error(monkeypatch) -> None:
    def fake_post(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
        raise provider_runtime.ProviderUnavailableError("OpenRouter request failed with status 429.")

    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setattr(provider_runtime, "_post_openrouter_chat", fake_post)
    client = TestClient(app)

    response = client.post(
        "/provider-config/openrouter/prompt",
        json={"prompt": "Say OK.", "model": "mistralai/mistral-7b-instruct:free"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "OpenRouter request failed with status 429."
    assert "test-openrouter-key" not in str(response.json())


def test_mocked_openai_compatible_provider_prompt_success(monkeypatch) -> None:
    captured: list[dict[str, Any]] = []

    def fake_post(url: str, headers: dict[str, str], payload: dict[str, Any], provider_label: str) -> dict[str, Any]:
        captured.append({"url": url, "headers": headers, "payload": payload, "provider_label": provider_label})
        return {
            "choices": [{"message": {"content": f"OK from {provider_label}"}}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 3},
        }

    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("MINIMAX_API_KEY", "test-minimax-key")
    monkeypatch.setenv("XAI_API_KEY", "test-xai-key")
    monkeypatch.setattr(provider_runtime, "_post_provider_json", fake_post)
    client = TestClient(app)

    cases = [
        ("openai", "gpt-5-mini", "gpt-5-mini", "https://api.openai.com/v1/chat/completions"),
        ("groq", "groq/llama-3.3-70b-versatile", "llama-3.3-70b-versatile", "https://api.groq.com/openai/v1/chat/completions"),
        ("minimax", "minimax/MiniMax-M2.5", "MiniMax-M2.5", "https://api.minimax.io/v1/chat/completions"),
        ("xai", "xai/grok-4", "grok-4", "https://api.x.ai/v1/chat/completions"),
    ]
    for provider_id, model, request_model, url in cases:
        response = client.post(f"/provider-config/{provider_id}/prompt", json={"prompt": "Say OK.", "model": model})
        assert response.status_code == 200
        payload = response.json()
        assert payload["provider"] == provider_id
        assert payload["model"] == model
        assert payload["request_model"] == request_model
        assert payload["response"].startswith("OK from")
        assert captured[-1]["url"] == url
        assert captured[-1]["payload"] == {"model": request_model, "messages": [{"role": "user", "content": "Say OK."}], "stream": False}

    serialized = str([item["headers"] for item in captured])
    assert "test-openai-key" not in serialized.replace("Bearer test-openai-key", "")


def test_mocked_anthropic_provider_prompt_success(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_post(url: str, headers: dict[str, str], payload: dict[str, Any], provider_label: str) -> dict[str, Any]:
        captured.update({"url": url, "headers": headers, "payload": payload, "provider_label": provider_label})
        return {"content": [{"type": "text", "text": "OK from Anthropic"}], "usage": {"input_tokens": 4}}

    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setattr(provider_runtime, "_post_provider_json", fake_post)
    client = TestClient(app)

    response = client.post("/provider-config/anthropic/prompt", json={"prompt": "Say OK.", "model": "claude-sonnet-4-5"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "anthropic"
    assert payload["response"] == "OK from Anthropic"
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["payload"]["max_tokens"] == 1024
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    assert "test-anthropic-key" not in str(response.json())


def test_mocked_google_provider_prompt_success(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_post(url: str, headers: dict[str, str], payload: dict[str, Any], provider_label: str) -> dict[str, Any]:
        captured.update({"url": url, "headers": headers, "payload": payload, "provider_label": provider_label})
        return {
            "candidates": [{"content": {"parts": [{"text": "OK from Gemini"}]}}],
            "usageMetadata": {"promptTokenCount": 4},
        }

    monkeypatch.setenv("SPARKBOT_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setattr(provider_runtime, "_post_provider_json", fake_post)
    client = TestClient(app)

    response = client.post("/provider-config/google/prompt", json={"prompt": "Say OK.", "model": "gemini/gemini-2.0-flash"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "google"
    assert payload["request_model"] == "gemini-2.0-flash"
    assert payload["response"] == "OK from Gemini"
    assert captured["url"] == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=test-google-key"
    assert captured["payload"] == {"contents": [{"parts": [{"text": "Say OK."}]}]}
    assert "test-google-key" not in str(response.json())
