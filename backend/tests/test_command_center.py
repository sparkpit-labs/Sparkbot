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


def test_default_sensitive_storage_stays_outside_checkout_after_credential_save(tmp_path, monkeypatch) -> None:
    from app.api import command_center

    checkout = tmp_path / "checkout"
    checkout.mkdir()
    xdg_data = tmp_path / "xdg-data"
    monkeypatch.chdir(checkout)
    monkeypatch.delenv("SPARKBOT_DATA_DIR", raising=False)
    monkeypatch.delenv("SPARKBOT_SECRETS_DIR", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(xdg_data))
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat/models/config",
        json={"providers": {"openrouter_api_key": "outside-checkout-secret"}},
    )

    assert response.status_code == 200
    assert "outside-checkout-secret" not in str(response.json())
    expected_secret_path = xdg_data / "sparkbot" / "command-center" / "secrets.json"
    assert command_center._secrets_path() == expected_secret_path
    assert expected_secret_path.exists()
    assert (checkout / "data" / "command-center" / "config.json").exists()
    assert not (checkout / "data" / "command-center" / "secrets.json").exists()


def test_sensitive_storage_override_can_be_separate_from_data_dir(tmp_path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    sensitive_dir = tmp_path / "sensitive"
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(config_dir))
    monkeypatch.setenv("SPARKBOT_SECRETS_DIR", str(sensitive_dir))
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat/models/config",
        json={"providers": {"openrouter_api_key": "override-secret-value"}},
    )

    assert response.status_code == 200
    payload = response.json()
    openrouter = next(provider for provider in payload["providers"] if provider["id"] == "openrouter")
    assert openrouter["configured"] is True
    assert "override-secret-value" not in str(payload)
    assert (config_dir / "config.json").exists()
    assert (sensitive_dir / "secrets.json").exists()
    assert not (config_dir / "secrets.json").exists()


def test_openrouter_model_refresh_persists_catalog_without_credential_echo(tmp_path, monkeypatch) -> None:
    from app.api import command_center

    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = TestClient(app)
    credential = "unit-test-credential-value"

    class FakeResponse:
        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self._payload

    class FakeClient:
        def __init__(self, timeout: float | None = None) -> None:
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def get(self, url: str, headers: dict | None = None) -> FakeResponse:
            if url.endswith("/api/tags"):
                return FakeResponse({"models": []})
            assert url == "https://openrouter.ai/api/v1/models"
            assert (headers or {}).get("Authorization") == f"Bearer {credential}"
            return FakeResponse(
                {
                    "data": [
                        {
                            "id": "test/fresh-paid-model",
                            "name": "Fresh Paid Model",
                            "context_length": 8192,
                            "pricing": {"prompt": "0.0001", "completion": "0.0002"},
                        },
                        {
                            "id": "test/fresh-free-model:free",
                            "name": "Fresh Free Model",
                            "context_length": 4096,
                            "pricing": {"prompt": "0", "completion": "0"},
                        },
                    ]
                }
            )

    monkeypatch.setattr(command_center.httpx, "AsyncClient", FakeClient)

    save_response = client.post(
        "/api/v1/chat/models/config",
        json={"providers": {"openrouter_api_key": credential}},
    )
    assert save_response.status_code == 200
    assert credential not in str(save_response.json())

    refresh_response = client.get("/api/v1/chat/openrouter/models")

    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()
    refreshed_ids = [model["id"] for model in refresh_payload["models"]]
    assert refreshed_ids == ["openrouter/test/fresh-free-model:free", "openrouter/test/fresh-paid-model"]
    assert credential not in str(refresh_payload)

    controls = refresh_payload["controls"]
    openrouter = next(provider for provider in controls["providers"] if provider["id"] == "openrouter")
    assert openrouter["configured"] is True
    assert openrouter["models"] == refreshed_ids
    assert controls["model_labels"]["openrouter/test/fresh-free-model:free"] == "Fresh Free Model"

    readback = client.get("/api/v1/chat/models/config").json()
    readback_openrouter = next(provider for provider in readback["providers"] if provider["id"] == "openrouter")
    assert readback_openrouter["models"] == refreshed_ids
    assert readback["model_labels"]["openrouter/test/fresh-paid-model"] == "Fresh Paid Model"
    assert credential not in str(readback)

    select_response = client.post(
        "/api/v1/chat/models/config",
        json={"default_selection": {"provider": "openrouter", "model": "openrouter/test/fresh-free-model:free"}},
    )
    assert select_response.status_code == 200
    assert select_response.json()["default_selection"] == {
        "provider": "openrouter",
        "model": "openrouter/test/fresh-free-model:free",
        "label": "Fresh Free Model",
    }

    events = client.get("/api/events").json()["events"]
    assert "provider.model_catalog.refreshed" in {event["event_type"] for event in events}
    assert credential not in str(events)


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


def test_custom_agent_profile_persists_server_side_and_redacts_sensitive_text(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/chat/agents",
        json={
            "name": "Risk Lens",
            "description": "Reviews risk token raw-description-secret",
            "system_prompt": "Use RISK-LENS-CUSTOM review. api_key=raw-agent-key",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "risk_lens"
    assert created["label"] == "Risk Lens"
    assert created["description"] == "Reviews risk token [redacted]"
    assert created["system_prompt"] == "Use RISK-LENS-CUSTOM review. api_key=[redacted]"
    assert "raw-description-secret" not in str(created)
    assert "raw-agent-key" not in str(created)

    update_response = client.patch(
        "/api/v1/chat/agents/risk_lens",
        json={
            "description": "Edited server-side profile.",
            "system_prompt": "Use EDITED-RISK-LENS instructions. secret:raw-edit-secret",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["description"] == "Edited server-side profile."
    assert updated["system_prompt"] == "Use EDITED-RISK-LENS instructions. secret:[redacted]"
    assert "raw-edit-secret" not in str(updated)

    packaged_update = client.patch("/api/v1/chat/agents/researcher", json={"description": "Override packaged agent"})
    assert packaged_update.status_code == 400

    second_client = TestClient(app)
    agents_response = second_client.get("/api/v1/chat/agents")
    assert agents_response.status_code == 200
    risk_lens = next(agent for agent in agents_response.json()["agents"] if agent["name"] == "risk_lens")
    assert risk_lens["description"] == "Edited server-side profile."
    assert risk_lens["system_prompt"] == "Use EDITED-RISK-LENS instructions. secret:[redacted]"

    config_response = second_client.get("/api/v1/chat/models/config")
    assert config_response.status_code == 200
    config_agent = next(agent for agent in config_response.json()["available_agents"] if agent["name"] == "risk_lens")
    assert config_agent["system_prompt"] == "Use EDITED-RISK-LENS instructions. secret:[redacted]"

    events = second_client.get("/api/events").json()["events"]
    assert "raw-agent-key" not in str(events)
    assert "raw-edit-secret" not in str(events)
    assert "EDITED-RISK-LENS" not in str(events)


def test_agent_invite_route_rejects_unsupported_subscription_auth_modes(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/chat/agents",
        json={"name": "Invite Guard", "description": "Guard invite auth", "system_prompt": "Stay safe."},
    )
    assert create_response.status_code == 201

    metadata_only_auth = client.post(
        "/api/v1/chat/agents/invite_guard/invite-route",
        json={
            "model": "openrouter/meta-llama/llama-3.1-70b-instruct:free",
            "api_key": "invite-route-secret",
            "auth_mode": "codex_sub",
        },
    )
    assert metadata_only_auth.status_code == 400
    assert "Unsupported invite route auth mode" in metadata_only_auth.json()["detail"]

    unsupported_model = client.post(
        "/api/v1/chat/agents/invite_guard/invite-route",
        json={
            "model": "openai-codex/gpt-5.3-codex",
            "api_key": "invite-route-secret",
            "auth_mode": "api_key",
        },
    )
    assert unsupported_model.status_code == 400
    assert "Subscription-only invite routes" in unsupported_model.json()["detail"]

    wrong_oauth_provider = client.post(
        "/api/v1/chat/agents/invite_guard/invite-route",
        json={
            "model": "openrouter/meta-llama/llama-3.1-70b-instruct:free",
            "api_key": "invite-route-secret",
            "auth_mode": "oauth",
        },
    )
    assert wrong_oauth_provider.status_code == 400
    assert "OAuth invite auth mode" in wrong_oauth_provider.json()["detail"]

    anthropic_oauth = client.post(
        "/api/v1/chat/agents/invite_guard/invite-route",
        json={
            "model": "claude-3-5-sonnet-latest",
            "api_key": "invite-route-secret",
            "auth_mode": "oauth",
        },
    )
    assert anthropic_oauth.status_code == 200
    assert anthropic_oauth.json()["invite_route"] == {
        "route": "anthropic",
        "model": "claude-3-5-sonnet-latest",
        "auth_mode": "oauth",
        "credential_configured": True,
    }
    assert "invite-route-secret" not in str(client.get("/api/events").json())


def test_agent_invite_route_persists_server_side_without_secret_echo(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/chat/agents",
        json={"name": "Invite Lens", "description": "Invite route agent", "system_prompt": "Use invite route context."},
    )
    assert create_response.status_code == 201

    invite_response = client.post(
        "/api/v1/chat/agents/invite_lens/invite-route",
        json={
            "model": "openrouter/meta-llama/llama-3.1-70b-instruct:free",
            "api_key": "invite-route-secret",
            "auth_mode": "api_key",
        },
    )

    assert invite_response.status_code == 200
    payload = invite_response.json()
    assert payload["name"] == "invite_lens"
    assert payload["configured"] is True
    assert payload["invite_route"] == {
        "route": "openrouter",
        "model": "openrouter/meta-llama/llama-3.1-70b-instruct:free",
        "auth_mode": "api_key",
        "credential_configured": True,
    }
    assert "invite-route-secret" not in str(payload)

    config_response = client.get("/api/v1/chat/models/config")
    assert config_response.status_code == 200
    invite_agent = next(agent for agent in config_response.json()["available_agents"] if agent["name"] == "invite_lens")
    assert invite_agent["invite_route"]["credential_configured"] is True
    assert invite_agent["invite_route"]["model"] == "openrouter/meta-llama/llama-3.1-70b-instruct:free"
    assert "invite-route-secret" not in str(config_response.json())

    second_client = TestClient(app)
    persisted = next(agent for agent in second_client.get("/api/v1/chat/agents").json()["agents"] if agent["name"] == "invite_lens")
    assert persisted["invite_route"]["route"] == "openrouter"
    assert persisted["invite_route"]["credential_configured"] is True

    events = second_client.get("/api/events").json()["events"]
    assert "agent.invite_route.updated" in {event["event_type"] for event in events}
    assert "invite-route-secret" not in str(events)

    clear_response = second_client.delete("/api/v1/chat/agents/invite_lens/invite-route")
    assert clear_response.status_code == 200
    assert clear_response.json()["configured"] is False
    cleared_config = second_client.get("/api/v1/chat/models/config").json()
    cleared_agent = next(agent for agent in cleared_config["available_agents"] if agent["name"] == "invite_lens")
    assert "invite_route" not in cleared_agent
    assert "invite-route-secret" not in str(cleared_config)
