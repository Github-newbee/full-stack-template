from sqlalchemy import Engine, text

from app.core.snowflake import next_snowflake_id


ID_COLUMNS = {
    "permissions": ["id"],
    "roles": ["id"],
    "users": ["id"],
    "tasks": ["id", "created_by_id"],
    "assets": ["id", "uploaded_by_id"],
    "role_permissions": ["role_id", "permission_id"],
    "user_roles": ["user_id", "role_id"],
}

PRIMARY_ID_TABLES = ["permissions", "roles", "users", "tasks", "assets"]
LEGACY_ID_MAX = 2**31 - 1

ID_REFERENCES = {
    "permissions": [("role_permissions", "permission_id")],
    "roles": [("role_permissions", "role_id"), ("user_roles", "role_id")],
    "users": [
        ("user_roles", "user_id"),
        ("tasks", "created_by_id"),
        ("assets", "uploaded_by_id"),
    ],
    "tasks": [],
    "assets": [],
}


FOREIGN_KEYS = [
    (
        "role_permissions",
        "role_permissions_role_id_fkey",
        "role_id",
        "roles",
        "id",
        "ON DELETE CASCADE",
    ),
    (
        "role_permissions",
        "role_permissions_permission_id_fkey",
        "permission_id",
        "permissions",
        "id",
        "ON DELETE CASCADE",
    ),
    ("user_roles", "user_roles_user_id_fkey", "user_id", "users", "id", "ON DELETE CASCADE"),
    ("user_roles", "user_roles_role_id_fkey", "role_id", "roles", "id", "ON DELETE CASCADE"),
    ("tasks", "tasks_created_by_id_fkey", "created_by_id", "users", "id", ""),
    ("assets", "assets_uploaded_by_id_fkey", "uploaded_by_id", "users", "id", ""),
]


def ensure_bigint_ids(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as connection:
        existing_tables = set(
            connection.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    """
                )
            ).scalars()
        )
        if not existing_tables:
            return

        for table, constraint, *_ in FOREIGN_KEYS:
            if table in existing_tables:
                connection.execute(
                    text(f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{constraint}"')
                )

        for table, columns in ID_COLUMNS.items():
            if table not in existing_tables:
                continue
            existing_columns = set(
                connection.execute(
                    text(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = :table
                        """
                    ),
                    {"table": table},
                ).scalars()
            )
            for column in columns:
                if column in existing_columns:
                    connection.execute(
                        text(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" TYPE BIGINT')
                    )

        _drop_legacy_id_defaults(connection, existing_tables)
        _remap_legacy_ids(connection, existing_tables)

        for table, constraint, column, ref_table, ref_column, on_delete in FOREIGN_KEYS:
            if table not in existing_tables or ref_table not in existing_tables:
                continue
            if _constraint_exists(connection, table, constraint):
                continue
            connection.execute(
                text(
                    f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint}" '
                    f'FOREIGN KEY ("{column}") REFERENCES "{ref_table}" ("{ref_column}") {on_delete}'
                )
            )


def _drop_legacy_id_defaults(connection, existing_tables: set[str]) -> None:
    for table in PRIMARY_ID_TABLES:
        if table not in existing_tables:
            continue
        connection.execute(text(f'ALTER TABLE "{table}" ALTER COLUMN "id" DROP DEFAULT'))


def _remap_legacy_ids(connection, existing_tables: set[str]) -> None:
    for table in PRIMARY_ID_TABLES:
        if table not in existing_tables:
            continue

        legacy_ids = list(
            connection.execute(
                text(f'SELECT id FROM "{table}" WHERE id > 0 AND id <= :max_id ORDER BY id'),
                {"max_id": LEGACY_ID_MAX},
            ).scalars()
        )
        if not legacy_ids:
            continue

        id_map = {legacy_id: next_snowflake_id() for legacy_id in legacy_ids}
        for old_id, new_id in id_map.items():
            for ref_table, ref_column in ID_REFERENCES[table]:
                if ref_table in existing_tables:
                    connection.execute(
                        text(
                            f'UPDATE "{ref_table}" SET "{ref_column}" = :new_id '
                            f'WHERE "{ref_column}" = :old_id'
                        ),
                        {"old_id": old_id, "new_id": new_id},
                    )

            connection.execute(
                text(f'UPDATE "{table}" SET id = :new_id WHERE id = :old_id'),
                {"old_id": old_id, "new_id": new_id},
            )


def _constraint_exists(connection, table: str, constraint: str) -> bool:
    return bool(
        connection.execute(
            text(
                """
                SELECT 1
                FROM pg_constraint
                WHERE conrelid = CAST(:table AS regclass) AND conname = :constraint
                """
            ),
            {"table": table, "constraint": constraint},
        ).first()
    )
