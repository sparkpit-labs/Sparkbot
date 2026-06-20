from pathlib import Path
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import app
from app.services import local_model_adapter


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("SPARKBOT_LOCAL_MODELS_ENABLED", raising=False)
    monkeypatch.delenv("SPARKBOT_OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("SPARKBOT_OLLAMA_MODEL", raising=False)
    return TestClient(app)


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


def test_status_default_disabled(client: TestClient) -> None:
    response = client.get("/local-models/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "disabled-by-default"
    assert payload["local_models_enabled"] is False
    assert payload["adapter"] == "ollama"
    assert payload["base_url"] == "http://127.0.0.1:11434"
    assert payload["base_url_policy"] == "localhost-only"
    assert payload["configured_model"] is None
    assert payload["prompt_calls"] == "disabled"
    assert payload["credentials"] == "not-supported"
    assert payload["external_network"] == "not-supported"


def test_prompt_endpoint_returns_403_when_disabled(client: TestClient) -> None:
    response = client.post("/local-models/ollama/prompt", json={"prompt": "hello", "model": "llama3.2"})

    assert response.status_code == 403


def test_enabled_status_reports_reachable_local_ollama(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "true")
    monkeypatch.setenv("SPARKBOT_OLLAMA_MODEL", "llama3.2")

    def fake_request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 2) -> dict[str, Any]:
        assert url == "http://127.0.0.1:11434/api/tags"
        assert payload is None
        return {"models": []}

    monkeypatch.setattr(local_model_adapter, "_request_json", fake_request_json)

    payload = client.get("/local-models/status").json()

    assert payload["status"] == "available-local-only"
    assert payload["local_models_enabled"] is True
    assert payload["prompt_calls"] == "enabled-local-only"
    assert payload["configured_model"] == "llama3.2"
    assert payload["ollama_reachable"] is True


def test_enabled_status_reports_unavailable_without_failing(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "yes")
    monkeypatch.setenv("SPARKBOT_OLLAMA_MODEL", "llama3.2")

    def fake_request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 2) -> dict[str, Any]:
        raise local_model_adapter.LocalModelUnavailableError("Local Ollama endpoint is unavailable.")

    monkeypatch.setattr(local_model_adapter, "_request_json", fake_request_json)

    payload = client.get("/local-models/status").json()

    assert payload["status"] == "unavailable"
    assert payload["local_models_enabled"] is True
    assert payload["ollama_reachable"] is False


def test_non_localhost_ollama_base_url_is_rejected(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "true")
    monkeypatch.setenv("SPARKBOT_OLLAMA_BASE_URL", "http://192.0.2.10:11434")

    status_payload = client.get("/local-models/status").json()
    assert status_payload["status"] == "unavailable"
    assert status_payload["base_url"] is None
    assert "localhost" in status_payload["configuration_error"]

    response = client.post("/local-models/ollama/prompt", json={"prompt": "hello", "model": "llama3.2"})
    assert response.status_code == 400


def test_prompt_validation_and_safe_model_names(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "true")

    assert client.post("/local-models/ollama/prompt", json={"prompt": "", "model": "llama3.2"}).status_code == 422
    assert client.post("/local-models/ollama/prompt", json={"prompt": "hello", "model": "bad model"}).status_code == 400
    assert client.post("/local-models/ollama/prompt", json={"prompt": "hello"}).status_code == 400


def test_mocked_ollama_success_returns_local_response(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "1")

    def fake_request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
        assert url == "http://127.0.0.1:11434/api/generate"
        assert payload == {"model": "llama3.2", "prompt": "Keep this local.", "stream": False}
        return {"response": "Local response only.", "done": True}

    monkeypatch.setattr(local_model_adapter, "_request_json", fake_request_json)

    response = client.post("/local-models/ollama/prompt", json={"prompt": "Keep this local.", "model": "llama3.2"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["adapter"] == "ollama"
    assert payload["base_url_policy"] == "localhost-only"
    assert payload["model"] == "llama3.2"
    assert payload["response"] == "Local response only."
    assert payload["stored_message"] is None


def test_mocked_ollama_failure_returns_safe_error(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "true")

    def fake_request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
        raise local_model_adapter.LocalModelUnavailableError("Local Ollama endpoint is unavailable.")

    monkeypatch.setattr(local_model_adapter, "_request_json", fake_request_json)

    response = client.post("/local-models/ollama/prompt", json={"prompt": "hello", "model": "llama3.2"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Local Ollama endpoint is unavailable."


def test_local_assistant_response_persists_when_session_id_is_provided(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_LOCAL_MODELS_ENABLED", "true")
    created_session = client.post("/local/chat/sessions", json={"title": "Local model session"}).json()

    def fake_request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
        return {"response": "Stored local assistant response.", "done": True}

    monkeypatch.setattr(local_model_adapter, "_request_json", fake_request_json)

    response = client.post(
        "/local-models/ollama/prompt",
        json={"session_id": created_session["id"], "prompt": "hello", "model": "llama3.2"},
    )

    assert response.status_code == 200
    assert response.json()["stored_message"]["role"] == "assistant-local"
    session = client.get(f"/local/chat/sessions/{created_session['id']}").json()
    assert session["messages"][-1]["role"] == "assistant-local"
    assert session["messages"][-1]["content"] == "Stored local assistant response."


def test_local_model_routes_do_not_add_cloud_or_execution_paths(client: TestClient) -> None:
    route_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    forbidden_paths = {
        "/local-models/cloud/prompt",
        "/local-models/provider-token",
        "/local-models/execute",
        "/local-models/connectors/send",
    }

    assert route_paths.isdisjoint(forbidden_paths)
    for path in forbidden_paths:
        assert client.post(path, json={}).status_code == 404


def test_status_response_has_no_secret_value_fields(client: TestClient) -> None:
    payload = client.get("/local-models/status").json()
    blocked = ("api_key", "apikey", "password", "secret")
    for key in _walk_keys(payload):
        normalized = key.lower().replace("-", "_")
        assert not any(fragment in normalized for fragment in blocked)
