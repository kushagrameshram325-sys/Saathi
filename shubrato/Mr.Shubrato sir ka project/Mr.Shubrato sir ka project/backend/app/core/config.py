"""
SAATHI application configuration.

Settings are loaded from environment variables (and an optional .env file).
Defaults work for local development with no extra configuration required.

Environment variables
---------------------
APP_NAME        Display name (default: "SAATHI API")
API_PREFIX      URL prefix for all API routes (default: "/api/v1")
DATABASE_URL    SQLAlchemy DB URL (default: "sqlite:///./saathi.db")
CORS_ORIGINS    Comma-separated allowed CORS origins
                (default: localhost:5500, 127.0.0.1:5500, :8000)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic-settings model loaded from environment / .env file."""

    app_name: str = "SAATHI API"
    api_prefix: str = "/api/v1"

    # SQLite for development; swap to a PostgreSQL URL for production.
    database_url: str = "sqlite:///./saathi.db"

    # Comma-separated list of allowed CORS origins.
    cors_origins: str = (
        "http://localhost:5500,"
        "http://127.0.0.1:5500,"
        "http://localhost:8000,"
        "http://127.0.0.1:8000,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
