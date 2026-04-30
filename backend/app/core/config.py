from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SnipyMart ERP"
    environment: Literal["development", "test", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7
    backend_cors_origins: str = "http://localhost:3000"
    first_superuser_email: str = "admin@snipymart.in"
    first_superuser_password: str = "Admin@12345"
    first_cashier_email: str = "cashier@snipymart.in"
    first_cashier_password: str = "Cashier@12345"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
