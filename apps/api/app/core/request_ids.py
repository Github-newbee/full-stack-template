from fastapi import HTTPException

from app.core.snowflake import parse_snowflake_id


def parse_request_id(value: str) -> int:
    try:
        return parse_snowflake_id(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid snowflake id") from exc


def parse_request_ids(values: list[str]) -> list[int]:
    return [parse_request_id(value) for value in values]
