import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import model_execution


PROVIDER_ENVS = [
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "MINIMAX_API_KEY",
    "XAI_API_KEY",
]


def _clear_provider_env(monkeypatch) -> None:
    for name in PROVIDER_ENVS:
        monkeypatch.delenv(name, raising=False)


def _save_openrouter_credential(client: TestClient, credential: str = "unit-test-credential-value") -> None:
    response = client.post("/api/v1/chat/models/config", json={"providers": {"openrouter_api_key": credential}})
    assert response.status_code == 200


def test_chat_provider_success_path_uses_selected_command_center_route(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    calls: list[dict[str, object]] = []

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        calls.append({"url": url, "headers": headers, "payload": payload, "timeout": timeout_seconds})
        return {"choices": [{"message": {"content": "Mocked provider response."}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    response = client.post("/api/chat/messages", json={"content": "Summarize this safely."})

    assert response.status_code == 201
    payload = response.json()
    assert payload["assistant_message"]["content"] == "Mocked provider response."
    assert payload["model_execution"]["status"] == "success"
    assert payload["route"]["provider"] == "openrouter"
    assert payload["route"]["model"] == "openrouter/openai/gpt-4o-mini"
    assert calls
    assert calls[0]["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert calls[0]["payload"]["model"] == "openai/gpt-4o-mini"

    events = client.get("/api/events?event_type=model.call.completed").json()["events"]
    assert events
    assert events[0]["payload"]["provider"] == "openrouter"
    assert events[0]["payload"]["status"] == "success"


def test_chat_model_route_tracks_updated_default_selection(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    calls: list[dict[str, object]] = []

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        calls.append({"url": url, "headers": headers, "payload": payload})
        return {"choices": [{"message": {"content": "OpenAI route response."}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    config_response = client.post(
        "/api/v1/chat/models/config",
        json={
            "default_selection": {"provider": "openai", "model": "gpt-4o-mini"},
            "providers": {"openai_api_key": "unit-test-credential-value"},
        },
    )
    assert config_response.status_code == 200

    response = client.post("/api/chat/messages", json={"content": "Use the selected route."})

    assert response.status_code == 201
    payload = response.json()
    assert payload["route"]["provider"] == "openai"
    assert payload["route"]["model"] == "gpt-4o-mini"
    assert payload["assistant_message"]["content"] == "OpenAI route response."
    assert calls[0]["url"] == "https://api.openai.com/v1/chat/completions"
    assert calls[0]["payload"]["model"] == "gpt-4o-mini"


def test_chat_provider_error_is_user_safe_and_does_not_expose_secret(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    credential = "unit-test-credential-value"

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        request = httpx.Request("POST", url)
        response = httpx.Response(502, request=request)
        raise httpx.HTTPStatusError("provider failed", request=request, response=response)

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client, credential)

    response = client.post("/api/chat/messages", json={"content": "Try provider error path."})

    assert response.status_code == 201
    payload = response.json()
    assert payload["model_execution"]["status"] == "error"
    assert "Provider request failed" in payload["assistant_message"]["content"]
    assert credential not in str(payload)

    events = client.get("/api/events").json()["events"]
    assert credential not in str(events)
    failed = next(event for event in events if event["event_type"] == "model.call.failed")
    assert failed["payload"]["http_status"] == 502
    assert "headers" not in failed["payload"]
    assert "messages" not in failed["payload"]


def test_chat_provider_timeout_is_user_safe(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    response = client.post("/api/chat/messages", json={"content": "Try timeout path."})

    assert response.status_code == 201
    payload = response.json()
    assert payload["model_execution"]["status"] == "timeout"
    assert "timed out" in payload["assistant_message"]["content"]

    failed = client.get("/api/events?event_type=model.call.failed").json()["events"][0]
    assert failed["payload"]["status"] == "timeout"
    assert "prompt" not in failed["payload"]
    assert "content" not in failed["payload"]


def test_model_call_events_do_not_store_prompts_outputs_or_credentials(tmp_path, monkeypatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    credential = "unit-test-credential-value"

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        return {"choices": [{"message": {"content": "Provider output text."}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client, credential)

    response = client.post("/api/chat/messages", json={"content": "Private user prompt text."})
    assert response.status_code == 201

    events = client.get("/api/events?event_type=model.call.completed").json()["events"]
    assert events
    event_payload = events[0]["payload"]
    assert event_payload["output_chars"] == len("Provider output text.")
    assert "Private user prompt text." not in str(event_payload)
    assert "Provider output text." not in str(event_payload)
    assert credential not in str(event_payload)
    assert {"provider", "model", "status", "message_count", "output_chars", "duration_ms"} <= set(event_payload)


@pytest.mark.parametrize(
    ("expected_action", "model_output"),
    [
        ("external_send", "I will send email to everyone now."),
        ("scheduler_action", "I will schedule job for later follow-up."),
        ("device_action", "I will control device status now."),
    ],
)
def test_model_output_cannot_execute_protected_actions(tmp_path, monkeypatch, expected_action: str, model_output: str) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        return {"choices": [{"message": {"content": model_output}}]}

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    response = client.post("/api/chat/messages", json={"content": "Draft a safe update."})

    assert response.status_code == 201
    payload = response.json()
    assert payload["model_execution"]["status"] == "success"
    assert payload["blocked_action"] == expected_action
    assert "model response requested protected" in payload["assistant_message"]["content"]
    assert model_output not in payload["assistant_message"]["content"]

    events = client.get("/api/events").json()["events"]
    blocked = [event for event in events if event["event_type"] == "guardian.action_blocked" and event["payload"].get("source") == "model_output"]
    assert blocked
    assert blocked[0]["payload"]["action_type"] == expected_action
    assert blocked[0]["payload"]["requires_confirmation"] is True


@pytest.mark.parametrize(
    ("expected_action", "content"),
    [
        ("external_send", "send email to the team"),
        ("connector_action", "run connector sync now"),
        ("file_mutation", "write file output for me"),
        ("process_action", "start process for this task"),
        ("scheduler_action", "schedule job for later follow-up"),
        ("device_action", "control device status now"),
        ("room_execution", "start meeting engine for this room"),
    ],
)
def test_user_protected_request_fails_closed_before_model_dispatch(tmp_path, monkeypatch, expected_action: str, content: str) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))

    async def fake_post_json(url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict[str, object]:
        raise AssertionError("protected requests must not dispatch to providers")

    monkeypatch.setattr(model_execution, "_post_json", fake_post_json)
    client = TestClient(app)
    _save_openrouter_credential(client)

    response = client.post("/api/chat/messages", json={"content": content})

    assert response.status_code == 201
    payload = response.json()
    assert payload["blocked_action"] == expected_action
    assert payload["model_execution"]["status"] == "not_called"
    assert "No action was executed" in payload["assistant_message"]["content"]

    events = client.get("/api/events").json()["events"]
    blocked = [event for event in events if event["event_type"] == "guardian.action_blocked"]
    assert blocked
    assert blocked[0]["payload"]["action_type"] == expected_action
    assert not any(event["event_type"].startswith("model.call") for event in events)
