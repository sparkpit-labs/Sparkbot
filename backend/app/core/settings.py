from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Sparkbot"
    environment: str = "local"
    host: str = "127.0.0.1"
    port: int = 8000
    sparkbot_provider: str = "openai"
    sparkbot_model: str | None = None
    sparkbot_provider_timeout_seconds: float = 45.0

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    openai_compatible_base_url: str | None = None
    openai_compatible_api_key: str | None = None
    openai_compatible_model: str | None = None

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
