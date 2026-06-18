from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


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


def test_provider_config_status_is_static_preview() -> None:
    client = TestClient(app)
    response = client.get("/provider-config/status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "preview"
    assert payload["credential_storage"] == "not-implemented"
    assert payload["provider_calls"] == "not-implemented"
    assert payload["model_routing"] == "not-implemented"
    assert payload["providers"] == [
        {
            "id": "local",
            "label": "Local provider",
            "status": "planned",
            "notes": "Local provider configuration is planned. No runtime provider calls are made.",
        },
        {
            "id": "openai-compatible",
            "label": "OpenAI-compatible provider",
            "status": "guarded-future",
            "notes": "Cloud provider configuration will require explicit setup and safety gates.",
        },
        {
            "id": "anthropic-compatible",
            "label": "Anthropic-compatible provider",
            "status": "guarded-future",
            "notes": "Cloud provider configuration will require explicit setup and safety gates.",
        },
        {
            "id": "google-compatible",
            "label": "Google-compatible provider",
            "status": "guarded-future",
            "notes": "Cloud provider configuration will require explicit setup and safety gates.",
        },
        {
            "id": "custom-endpoint",
            "label": "Custom endpoint",
            "status": "guarded-future",
            "notes": "Custom endpoints are planned for future guarded configuration.",
        },
    ]


def test_provider_statuses_remain_non_runtime_contract_values() -> None:
    client = TestClient(app)
    payload = client.get("/provider-config/status").json()
    providers = _provider_by_id(payload)

    assert {provider["status"] for provider in payload["providers"]} <= ALLOWED_CAPABILITY_STATUSES
    assert all(provider["status"] != "available" for provider in payload["providers"])
    assert providers["local"]["status"] == "planned"
    assert providers["openai-compatible"]["status"] == "guarded-future"
    assert providers["anthropic-compatible"]["status"] == "guarded-future"
    assert providers["google-compatible"]["status"] == "guarded-future"
    assert providers["custom-endpoint"]["status"] == "guarded-future"


def test_provider_config_status_contains_no_secret_fields() -> None:
    client = TestClient(app)
    payload = client.get("/provider-config/status").json()
    disallowed_key_fragments = ("api_key", "apikey", "password", "token", "secret")

    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in disallowed_key_fragments)

    serialized = str(payload).lower()
    assert "provider_calls': 'not-implemented" in serialized
    assert "model_routing': 'not-implemented" in serialized
