from types import SimpleNamespace

from app.core.snowflake import next_snowflake_id
from app.schemas import RoleRead


def test_snowflake_id_is_large_integer() -> None:
    snowflake_id = next_snowflake_id()

    assert isinstance(snowflake_id, int)
    assert snowflake_id > 2**31


def test_read_schema_returns_id_as_string() -> None:
    snowflake_id = next_snowflake_id()
    role = SimpleNamespace(
        id=snowflake_id,
        name="admin",
        description="Full access",
        permissions=[],
    )

    payload = RoleRead.model_validate(role).model_dump()

    assert payload["id"] == str(snowflake_id)
