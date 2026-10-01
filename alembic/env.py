from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# Import database Base
from app.database import Base

# Import all models so Alembic can detect them
from app.models import Department, Employee, LeaveRequest

# Load environment variables
load_dotenv()

# Alembic Config object
config = context.config

# Get DATABASE_URL from .env
database_url = os.getenv("DATABASE_URL")

if database_url:
    config.set_main_option(
        "sqlalchemy.url",
        database_url
    )

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()