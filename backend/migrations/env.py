
from logging.config import fileConfig

from alembic import context

from app.db.database import Base, DATABASE_URL
from app.models import Role, User, AuditLog

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Registrar los modelos de SQLAlchemy
target_metadata = Base.metadata

# Utilizar la conexión definida en .env
database_url = DATABASE_URL.render_as_string(
    hide_password=False
)

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%")
)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = __import__(
        "sqlalchemy"
    ).create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
