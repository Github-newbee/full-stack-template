from functools import lru_cache
from pathlib import Path

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    app_name: str = "Full Stack Admin Template"
    app_env: str = "local"
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    database_url: str | None = None
    postgres_host: str | None = None
    postgres_port: int = 5432
    postgres_db: str = "app"
    postgres_user: str = "app"
    postgres_password: str = "app"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24

    storage_dir: Path = Path("storage")
    max_upload_mb: int = 20
    seed_admin: bool = True
    admin_username: str = "admin"
    admin_email: EmailStr | str = "admin@example.com"
    admin_password: str = "admin123456"
    admin_full_name: str = "Template Admin"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def sqlalchemy_database_url(self) -> str | URL:
        if self.database_url:
            return self.database_url

        if self.postgres_host:
            return URL.create(
                "postgresql+psycopg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_db,
            )

        return "sqlite:///./app.db"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
