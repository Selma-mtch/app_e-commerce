import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.core import normalize_database_url, Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Import project models so that `Base.metadata` is populated for autogenerate
try:
    # models package is at project root: models/db_models.py
    import models.db_models  # noqa: F401, E402
except Exception:
    # if import fails, continue; autogenerate will produce an empty migration
    pass

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def get_database_url() -> str | None:
    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    return normalize_database_url(url)


def run_migrations_offline() -> None:
    url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL must be set to run migrations in offline mode")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# def run_migrations_online() -> None:
#     url = get_database_url()
#     if not url:
#         raise RuntimeError("DATABASE_URL must be set to run migrations in online mode")

#     configuration = config.get_section(config.config_ini_section) or {}
#     configuration["url"] = url

#     connectable = engine_from_config(
#         configuration,
#         prefix="",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(connection=connection, target_metadata=target_metadata)

#         with context.begin_transaction():
#             context.run_migrations()

from sqlalchemy import create_engine


def run_migrations_online() -> None:
    url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL must be set to run migrations in online mode")

    connectable = create_engine(
        url,
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
