from app.core.migrate import ALEMBIC_VERSION_TABLE, APP_TABLES, should_stamp_existing_schema


def test_should_stamp_existing_schema_without_version_table() -> None:
    assert should_stamp_existing_schema(set(APP_TABLES))


def test_should_not_stamp_versioned_schema() -> None:
    assert not should_stamp_existing_schema(set(APP_TABLES) | {ALEMBIC_VERSION_TABLE})


def test_should_not_stamp_partial_schema() -> None:
    existing_tables = set(APP_TABLES)
    existing_tables.remove(next(iter(existing_tables)))

    assert not should_stamp_existing_schema(existing_tables)
