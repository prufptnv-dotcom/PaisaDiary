from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PaisaDiary API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://paisadiary:paisadiary@localhost:5432/paisadiary"
    # Development-only fallback. Production must inject a high-entropy secret.
    jwt_secret_key: str = "local-development-only-change-this-secret"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def reject_default_secret_in_production(self) -> "Settings":
        if self.environment.lower() == "production" and self.jwt_secret_key == (
            "local-development-only-change-this-secret"
        ):
            raise ValueError("JWT_SECRET_KEY must be set to a strong secret in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
