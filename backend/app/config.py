from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    app_name: str = "SiftMail API"
    environment: str = Field("development", env="APP_ENV")
    backend_host: str = Field("0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(8000, env="BACKEND_PORT")
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"], env="CORS_ORIGINS")
    classification_threshold: float = Field(0.55, env="CLASSIFICATION_THRESHOLD")
    spam_keywords: List[str] = Field(
        default_factory=lambda: ["lottery", "winner", "wire transfer", "urgent", "bitcoin", "password"],
        env="SPAM_KEYWORDS",
    )
    phishing_domains: List[str] = Field(
        default_factory=lambda: ["example-phish.com", "dodgy-payments.io"], env="PHISHING_DOMAINS"
    )

    @validator("cors_origins", "spam_keywords", "phishing_domains", pre=True)
    def split_csv(cls, value):
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
