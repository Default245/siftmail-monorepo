from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SiftMail API"
    environment: str = Field("development", alias="APP_ENV")
    backend_host: str = Field("0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(8000, alias="BACKEND_PORT")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], alias="CORS_ORIGINS")
    classification_threshold: float = Field(0.55, alias="CLASSIFICATION_THRESHOLD")
    spam_keywords: list[str] = Field(
        default_factory=lambda: ["lottery", "winner", "wire transfer", "urgent", "bitcoin", "password"],
        alias="SPAM_KEYWORDS",
    )
    phishing_domains: list[str] = Field(
        default_factory=lambda: ["example-phish.com", "dodgy-payments.io"],
        alias="PHISHING_DOMAINS",
    )

    @field_validator("cors_origins", "spam_keywords", "phishing_domains", mode="before")
    @classmethod
    def split_csv(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", populate_by_name=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
