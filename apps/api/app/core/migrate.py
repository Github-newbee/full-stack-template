from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app import models as _models  # noqa: F401
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.id_migration import ensure_bigint_ids
from app.core.seeding import seed_defaults

ALEMBIC_VERSION_TABLE = "alembic_version"
API_ROOT = Path(__file__).resolve().parents[2]
APP_TABLES = set(Base.metadata.tables)


def get_alembic_config() -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "migrations"))
    return config


def should_stamp_existing_schema(existing_tables: set[str]) -> bool:
    return ALEMBIC_VERSION_TABLE not in existing_tables and APP_TABLES.issubset(existing_tables)


def migrate_database() -> None:
    ensure_bigint_ids(engine)
    existing_tables = set(inspect(engine).get_table_names())
    alembic_config = get_alembic_config()
    if should_stamp_existing_schema(existing_tables):
        command.stamp(alembic_config, "head")
        return

    command.upgrade(alembic_config, "head")


def seed_initial_data() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        seed_defaults(
            db,
            admin_username=settings.admin_username,
            admin_email=str(settings.admin_email),
            admin_password=settings.admin_password,
            admin_full_name=settings.admin_full_name,
            seed_admin=settings.seed_admin,
        )


def run_startup_tasks() -> None:
    migrate_database()
    seed_initial_data()


if __name__ == "__main__":
    run_startup_tasks()
    print("Database migration and initial data are ready.")
