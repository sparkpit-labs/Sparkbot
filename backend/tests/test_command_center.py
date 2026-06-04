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
