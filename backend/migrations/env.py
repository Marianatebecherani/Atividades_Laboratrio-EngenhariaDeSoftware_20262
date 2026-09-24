from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401  (registra todas as tabelas no metadata)
from app.core.config import obter_configuracoes
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Usa a URL definida pelo chamador (ex.: testes) ou a DATABASE_URL da aplicação.
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", obter_configuracoes().database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL das migrações sem conectar ao banco."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica as migrações conectando ao banco."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
