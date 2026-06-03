from fastapi.testclient import TestClient

from app.main import app


def test_models_config_defaults_and_no_secret_values(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    response = client.get("/api/v1/chat/models/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["default_selection"]["provider"] == "openrouter"
    assert payload["default_selection"]["model"].startswith("openrouter/")
    assert any(provider["id"] == "ollama" for provider in payload["providers"])
    assert "available_agents" in payload
    assert "openrouter_api_key" not in str(payload).lower()


def test_provider_credential_is_saved_server_side_without_echo(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat/models/config",
        json={"providers": {"openrouter_api_key": "test-provider-secret"}},
    )

    assert response.status_code == 200
    payload = response.json()
    openrouter = next(provider for provider in payload["providers"] if provider["id"] == "openrouter")
    assert openrouter["configured"] is True
    assert "test-provider-secret" not in str(payload)
    assert (tmp_path / "secrets.json").exists()


def test_default_model_provider_must_match(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat/models/config",
        json={"default_selection": {"provider": "openai", "model": "ollama/phi4-mini"}},
    )

    assert response.status_code == 400
    assert "does not match" in response.json()["detail"]


def test_security_pin_and_status(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    save_response = client.post("/api/v1/chat/security/operator-pin", json={"pin": "123456"})
    assert save_response.status_code == 200

    status_response = client.get("/api/v1/chat/security/status")
    assert status_response.status_code == 200
    assert status_response.json()["operator"]["pin_configured"] is True


def test_spine_overview_route_exists(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    response = client.get("/api/v1/chat/spine/operator/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "available"
    assert payload["open_queue"] == []
