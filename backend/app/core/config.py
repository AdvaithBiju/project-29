import os
from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Blood Report Analyzer"
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/blood_reports",
        env="DATABASE_URL",
    )
    storage_dir: Path = Field(default=Path("storage"), env="STORAGE_DIR")
    upload_max_mb: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
