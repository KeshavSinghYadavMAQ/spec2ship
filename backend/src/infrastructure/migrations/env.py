"""Alembic migration environment (T010).

Imports every domain model module so `Base.metadata` is fully populated for autogenerate,
and reads the database URL from application settings so local dev (SQLite) and
production (Azure SQL Database via `mssql+pyodbc`) share one source of truth.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import all domain models so they register with Base.metadata for autogenerate.
from src.domain.admin.audit import AuditLogEntry  # noqa: F401
from src.domain.admin.rbac import UserRoleAssignment  # noqa: F401
from src.domain.alerting.models import StockAlert  # noqa: F401
from src.domain.alerting.policy_models import ProductLocationPolicy  # noqa: F401
from src.domain.inventory.integration_event import IntegrationEvent  # noqa: F401
from src.domain.inventory.models import InventoryPosition  # noqa: F401
from src.domain.replenishment.models import ReplenishmentRecommendation  # noqa: F401
from src.domain.transfer_balance.priority_models import StorePriorityProfile  # noqa: F401
from src.infrastructure.config import get_settings
from src.infrastructure.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
