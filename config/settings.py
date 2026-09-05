"""
Football Scanner AI - Application Settings
Centralized configuration via .env file
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Literal
from pathlib import Path


class Settings(BaseSettings):
    # Database
    db_mode: Literal["sqlite", "postgresql"] = "sqlite"
    sqlite_path: str = "./data/football_scanner.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "football_scanner"
    postgres_user: str = "postgres"
    postgres_password: str = "password"

    # API
    sports_api_key: str = ""
    sports_api_provider: str = "mock"

    # App
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = True
    log_level: str = "INFO"

    # Rule Engine
    # Para football-data.org gratuito: mínimo 60s (10 req/min)
    # Para mock: pode ser 30s ou menos
    rule_engine_interval: int = 60
    alert_retention_hours: int = 24

    @property
    def database_url(self) -> str:
        if self.db_mode == "sqlite":
            path = Path(self.sqlite_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{path.resolve()}"
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        if self.db_mode == "sqlite":
            path = Path(self.sqlite_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{path.resolve()}"
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
