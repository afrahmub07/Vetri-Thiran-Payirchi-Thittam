from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LegalEase"
    environment: str = "development"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    backend_url: str = "http://127.0.0.1:8000"

    cors_origins: str = (
        "http://localhost:8501,"
        "http://127.0.0.1:8501"
    )

    max_input_chars: int = 20000
    max_output_tokens: int = 12000
    temperature: float = 0.25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()