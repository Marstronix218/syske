import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Syske Scheduler"
    database_url: str = "sqlite:///./data.db"
    timezone: str = "America/Argentina/Buenos_Aires"
    enable_scheduler: bool = True
    fail_threshold: int = 3
    # default 9-13 local time
    scheduler_high_energy_window: tuple[int, int] = (9, 13)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    # Ensure SQLite URL is absolute when pointing to local file.
    # Resolve relative to the backend project directory
    # (this file's parent folder),
    # so running from different CWDs (root vs backend) uses the same DB path.
    if settings.database_url.startswith("sqlite:///./"):
        rel = settings.database_url.replace("sqlite:///./", "")
        base_dir = Path(__file__).resolve().parents[1]  # backend directory
        db_path = (base_dir / rel).resolve()
        settings.database_url = f"sqlite:///{db_path}"
    os.environ.setdefault("TZ", settings.timezone)
    return settings


settings = get_settings()
