import pathlib
import pymysql
pymysql.install_as_MySQLdb()
import sys
import alembic
from sqlalchemy import engine_from_config, pool, MetaData
from logging.config import fileConfig
import logging

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.util.cred_handler import get_secret
from app.db.models import Base

IGNORE_TABLES = ['celery_taskmeta', 'celery_tasksetmeta']
IGNORE_COLUMNS = ['summary']

def include_object(object, name, type_, reflected, compare_to):
    """
    Should you include this table or not?
    """

    if type_ == 'table' and (name in IGNORE_TABLES or object.info.get("skip_autogenerate", False)):
        return False

    elif type_ == "column" and (name in IGNORE_COLUMNS or object.info.get("skip_autogenerate", False)):
        return False

    return True



DATABASE_URL = get_secret("connection_string")

metadata = Base.metadata


# Alembic Config object, which provides access to values within the .ini file
config = alembic.context.config
target_metadata = metadata
# Interpret the config file for logging
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode
    """
    connectable = config.attributes.get("connection", None)
    config.set_main_option("sqlalchemy.url", str(DATABASE_URL))
    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool
        )

    with connectable.connect() as connection:
        alembic.context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object
        )
        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    """
    alembic.context.configure(url=str(DATABASE_URL), include_object=include_object)
    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()