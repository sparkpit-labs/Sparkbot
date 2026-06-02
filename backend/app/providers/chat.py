from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, cast

import httpx
from pydantic import BaseModel

from app.core.settings import Settings

ProviderName = Literal["openai", "openai_compatible", "ollama"]


class ChatProviderError(Exception):
    status_code = 502

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ProviderConfigError(ChatProviderError):
    status_code = 400


class ProviderTimeoutError(ChatProviderError):
    status_code = 504


class ProviderFailureError(ChatProviderError):
    status_code = 502


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatProviderResult(BaseModel):
    provider: ProviderName
    model: str
    content: str


class ProviderStatus(BaseModel):
    id: ProviderName
    label: str
    configured: bool
    model: str | None
    base_url_configured: bool
    message: str


class ProviderStatusPayload(BaseModel):
    selected_provider: ProviderName
    selected_model: str | None
    configured: bool
    message: str
    providers: list[ProviderStatus]


class ChatProviderAdapter(Protocol):
    async def complete(self, messages: list[ChatMessage], model: str) -> str:
        ...


@dataclass(frozen=True)
class OpenAIChatAdapter:
    api_key: str | None
    base_url: str
    timeout_seconds: float
    provider_label: str = "provider"

    async def complete(self, messages: list[ChatMessage], model: str) -> str:
        if not self.api_key:
            raise ProviderConfigError(f"{self.provider_label} API key is not configured.")
        return await _post_openai_compatible_chat(
            base_url=self.base_url,
            api_key=self.api_key,
            model=model,
            messages=messages,
            timeout_seconds=self.timeout_seconds,
        )


@dataclass(frozen=True)
class OpenAICompatibleChatAdapter:
    base_url: str | None
    api_key: str | None
    timeout_seconds: float

    async def complete(self, messages: list[ChatMessage], model: str) -> str:
        if not self.base_url:
            raise ProviderConfigError("OpenAI-compatible base URL is not configured.")
        return await _post_openai_compatible_chat(
            base_url=self.base_url,
            api_key=self.api_key,
            model=model,
            messages=messages,
            timeout_seconds=self.timeout_seconds,
        )


@dataclass(frozen=True)
class OllamaChatAdapter:
    base_url: str
    timeout_seconds: float

    async def complete(self, messages: list[ChatMessage], model: str) -> str:
        endpoint = f"{self.base_url.rstrip('/')}/api/chat"
        payload = {
            "model": model,
            "messages": [message.model_dump() for message in messages],
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(endpoint, json=payload)
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("Ollama did not respond before the request timed out.") from exc
        except httpx.RequestError as exc:
            raise ProviderFailureError("Ollama is unavailable at the configured local endpoint.") from exc

        if response.status_code == 404:
            raise ProviderFailureError("Ollama model was not found. Pull or configure the selected model.")
        if response.status_code >= 400:
            raise ProviderFailureError("Ollama returned an error for the chat request.")

        data = response.json()
        content = data.get("message", {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderFailureError("Ollama response did not include assistant content.")
        return content


class ChatProviderRouter:
    provider_labels: dict[ProviderName, str] = {
        "openai": "OpenAI",
        "openai_compatible": "OpenAI-compatible",
        "ollama": "Ollama",
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def status(self) -> ProviderStatusPayload:
        selected_provider = self._normalize_provider(self.settings.sparkbot_provider)
        selected_model = self.model_for(selected_provider, None)
        providers = [self.provider_status(provider) for provider in self.provider_labels]
        selected_status = next(provider for provider in providers if provider.id == selected_provider)
        return ProviderStatusPayload(
            selected_provider=selected_provider,
            selected_model=selected_model,
            configured=selected_status.configured,
            message=selected_status.message,
            providers=providers,
        )

    def provider_status(self, provider: ProviderName) -> ProviderStatus:
        model = self.model_for(provider, None)
        base_url_configured = self._base_url_configured(provider)
        missing = self._missing_config(provider, model)
        configured = not missing
        return ProviderStatus(
            id=provider,
            label=self.provider_labels[provider],
            configured=configured,
            model=model,
            base_url_configured=base_url_configured,
            message="Configured" if configured else missing,
        )

    async def complete(
        self,
        *,
        message: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> ChatProviderResult:
        normalized_provider = self._normalize_provider(provider or self.settings.sparkbot_provider)
        selected_model = self.model_for(normalized_provider, model)
        missing = self._missing_config(normalized_provider, selected_model)
        if missing:
            raise ProviderConfigError(missing)

        messages = [
            ChatMessage(
                role="system",
                content=(
                    "You are Sparkbot, a local-first AI workstation assistant. "
                    "Answer directly and keep implementation guidance practical."
                ),
            ),
            ChatMessage(role="user", content=message),
        ]
        adapter = self.adapter_for(normalized_provider)
        content = await adapter.complete(messages, selected_model)
        return ChatProviderResult(provider=normalized_provider, model=selected_model, content=content)

    def adapter_for(self, provider: ProviderName) -> ChatProviderAdapter:
        if provider == "openai":
            return OpenAIChatAdapter(
                api_key=_clean_optional(self.settings.openai_api_key),
                base_url=self.settings.openai_base_url,
                timeout_seconds=self.settings.sparkbot_provider_timeout_seconds,
                provider_label="OpenAI",
            )
        if provider == "openai_compatible":
            return OpenAICompatibleChatAdapter(
                base_url=_clean_optional(self.settings.openai_compatible_base_url),
                api_key=_clean_optional(self.settings.openai_compatible_api_key),
                timeout_seconds=self.settings.sparkbot_provider_timeout_seconds,
            )
        if provider == "ollama":
            return OllamaChatAdapter(
                base_url=self.settings.ollama_base_url,
                timeout_seconds=self.settings.sparkbot_provider_timeout_seconds,
            )
        raise ProviderConfigError(f"Unsupported provider '{provider}'.")

    def model_for(self, provider: ProviderName, override_model: str | None) -> str | None:
        if override_model and override_model.strip():
            return override_model.strip()
        if self.settings.sparkbot_model and self.settings.sparkbot_model.strip():
            return self.settings.sparkbot_model.strip()
        if provider == "openai":
            return self.settings.openai_model.strip()
        if provider == "openai_compatible":
            return _clean_optional(self.settings.openai_compatible_model)
        if provider == "ollama":
            return _clean_optional(self.settings.ollama_model)
        return None

    def _missing_config(self, provider: ProviderName, model: str | None) -> str:
        if not model:
            return f"{self.provider_labels[provider]} model is not configured."
        if provider == "openai" and not _clean_optional(self.settings.openai_api_key):
            return "OpenAI API key is not configured on the backend."
        if provider == "openai_compatible" and not _clean_optional(self.settings.openai_compatible_base_url):
            return "OpenAI-compatible base URL is not configured on the backend."
        if provider == "ollama" and not _clean_optional(self.settings.ollama_base_url):
            return "Ollama base URL is not configured on the backend."
        return ""

    def _base_url_configured(self, provider: ProviderName) -> bool:
        if provider == "openai":
            return bool(_clean_optional(self.settings.openai_base_url))
        if provider == "openai_compatible":
            return bool(_clean_optional(self.settings.openai_compatible_base_url))
        if provider == "ollama":
            return bool(_clean_optional(self.settings.ollama_base_url))
        return False

    def _normalize_provider(self, provider: str) -> ProviderName:
        normalized = provider.strip().lower()
        if normalized in self.provider_labels:
            return cast(ProviderName, normalized)
        raise ProviderConfigError("Unsupported provider. Use openai, openai_compatible, or ollama.")


async def _post_openai_compatible_chat(
    *,
    base_url: str,
    api_key: str | None,
    model: str,
    messages: list[ChatMessage],
    timeout_seconds: float,
) -> str:
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": [message.model_dump() for message in messages],
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
    except httpx.TimeoutException as exc:
        raise ProviderTimeoutError("Provider did not respond before the request timed out.") from exc
    except httpx.RequestError as exc:
        raise ProviderFailureError("Provider endpoint is unavailable or misconfigured.") from exc

    if response.status_code == 401:
        raise ProviderConfigError("Provider rejected the configured API key.")
    if response.status_code == 404:
        raise ProviderFailureError("Provider endpoint or model was not found.")
    if response.status_code >= 400:
        raise ProviderFailureError("Provider returned an error for the chat request.")

    data = response.json()
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderFailureError("Provider response did not include choices.")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise ProviderFailureError("Provider response did not include assistant content.")
    return content


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
