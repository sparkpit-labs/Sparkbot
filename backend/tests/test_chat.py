import pytest
from fastapi.testclient import TestClient

from app.api.chat import get_provider_router
from app.core.settings import Settings
from app.main import app
from app.providers.chat import (
    ChatProviderResult,
    ChatProviderRouter,
    OllamaChatAdapter,
    OpenAIChatAdapter,
    OpenAICompatibleChatAdapter,
)


class MockProviderRouter:
    def status(self):
        return {
            "selected_provider": "openai",
            "selected_model": "mock-model",
            "configured": True,
            "message": "Configured",
            "providers": [],
        }

    async def complete(self, *, message: str, provider: str | None = None, model: str | None = None):
        assert message == "Hello Sparkbot"
        return ChatProviderResult(provider="openai", model=model or "mock-model", content="Hello from the provider")


def test_chat_endpoint_returns_mocked_provider_response() -> None:
    app.dependency_overrides[get_provider_router] = lambda: MockProviderRouter()
    try:
        client = TestClient(app)
        response = client.post("/api/chat", json={"message": "Hello Sparkbot", "provider": "openai"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "provider": "openai",
        "model": "mock-model",
        "content": "Hello from the provider",
    }


def test_missing_openai_key_returns_safe_error() -> None:
    router = ChatProviderRouter(Settings(sparkbot_provider="openai", openai_api_key=None))
    app.dependency_overrides[get_provider_router] = lambda: router
    try:
        client = TestClient(app)
        response = client.post("/api/chat", json={"message": "Hello Sparkbot", "provider": "openai"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json() == {"detail": "OpenAI API key is not configured on the backend."}


@pytest.mark.parametrize(
    ("provider", "expected_adapter"),
    [
        ("openai", OpenAIChatAdapter),
        ("openai_compatible", OpenAICompatibleChatAdapter),
        ("ollama", OllamaChatAdapter),
    ],
)
def test_provider_adapter_selection(provider: str, expected_adapter: type) -> None:
    router = ChatProviderRouter(
        Settings(
            sparkbot_provider=provider,
            openai_api_key="test-key",
            openai_compatible_base_url="http://127.0.0.1:9000/v1",
            openai_compatible_model="compat-model",
            ollama_model="llama3.1",
        )
    )

    assert isinstance(router.adapter_for(provider), expected_adapter)


def test_provider_status_reports_all_required_providers() -> None:
    router = ChatProviderRouter(
        Settings(
            sparkbot_provider="openai_compatible",
            openai_compatible_base_url="http://127.0.0.1:9000/v1",
            openai_compatible_model="compat-model",
            ollama_model="llama3.1",
        )
    )

    status = router.status()

    assert status.selected_provider == "openai_compatible"
    assert status.selected_model == "compat-model"
    assert {provider.id for provider in status.providers} == {"openai", "openai_compatible", "ollama"}
    assert next(provider for provider in status.providers if provider.id == "openai_compatible").configured is True
