"""Configuration — reads all settings from environment variables via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = "dev-only-secret-key-change-me-please-32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./waqt.db"
    CORS_ORIGINS: str = "http://localhost:8000,http://localhost:3000"
    ENVIRONMENT: str = "development"
    VERCEL: int = 0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_vercel(self) -> bool:
        return self.VERCEL == 1 or self.ENVIRONMENT.lower() == "vercel"


@lru_cache
def get_settings() -> Settings:
    return Settings()
