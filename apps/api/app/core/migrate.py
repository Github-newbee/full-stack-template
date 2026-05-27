from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.id_migration import ensure_bigint_ids
from app.roles import seed_defaults


def migrate_database() -> None:
    ensure_bigint_ids(engine)
    Base.metadata.create_all(bind=engine)


def seed_initial_data() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        seed_defaults(
            db,
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
