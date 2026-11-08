from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PaisaDiary API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://paisadiary:paisadiary@localhost:5432/paisadiary"
    # Replace this with a high-entropy secret in .env before deployment.
    jwt_secret_key: str = "local-development-only-change-this-secret"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
