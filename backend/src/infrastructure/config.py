"""Environment/config management (T018).

Uses pydantic-settings so configuration is validated at process startup rather than
failing lazily deep in application code. Defaults favor local development (SQLite,
local Redis) while production deployments override via environment variables to point
at Azure SQL Database, Azure Cache for Redis, and Azure Service Bus per plan.md/research.md.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    environment: str = "local"

    # Storage (research.md: Azure SQL Database via mssql+pyodbc; SQLite fallback for local dev/tests)
    database_url: str = "sqlite:///./dev.db"

    # Azure Cache for Redis (research.md: suppression windows FR-003, evaluation locks FR-023,
    # rate-limit token buckets FR-024)
    redis_url: str = "redis://localhost:6379/0"

    # Azure Service Bus (research.md: inbound event queue + replay FR-022)
    service_bus_connection_string: str | None = None
    service_bus_queue_name: str = "inventory-events"

    # CORS - frontend dev origin
    cors_allow_origins: list[str] = ["http://localhost:5173"]

    # Rate limiting (FR-024)
    rate_limit_requests_per_window: int = 100
    rate_limit_window_seconds: int = 60

    # Cost guardrails (SC-008, Constitution VI)
    cost_ceiling_monthly_usd: float = 15_000.0
    cost_per_ingested_event_usd: float = 0.00005

    # Alert suppression default window (FR-003)
    alert_suppression_window_seconds: int = 900


@lru_cache
def get_settings() -> Settings:
    return Settings()
