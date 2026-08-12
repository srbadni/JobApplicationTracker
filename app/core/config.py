from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    """Configuration loaded from environment variables and an optional .env file."""

    app_name: str = "JobTracker API"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    @property
    def database_url(self) -> URL:
        """Build a safely escaped PostgreSQL connection URL."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one immutable-by-convention settings instance per process."""
    return Settings()
