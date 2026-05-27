from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_permission
from app.core.security import get_password_hash
from app.core.snowflake import parse_snowflake_id
from app.models import Role, User
from app.pagination import PageResponse
from app.schemas import UserCreate, UserRead, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


def parse_request_id(value: str) -> int:
    try:
        return parse_snowflake_id(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid snowflake id") from exc


def parse_request_ids(values: list[str]) -> list[int]:
    return [parse_request_id(value) for value in values]


@router.get(
    "",
    response_model=PageResponse[UserRead],
    dependencies=[Depends(require_permission("users.read"))],
)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PageResponse[UserRead]:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    users = db.scalars(
        select(User).order_by(User.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return PageResponse(items=list(users), total=total, page=page, page_size=page_size)


@router.post(
    "",
    response_model=UserRead,
    dependencies=[Depends(require_permission("users.write"))],
)
def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    existing = db.scalars(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    role_ids = parse_request_ids(payload.role_ids)
    roles = db.scalars(select(Role).where(Role.id.in_(role_ids))).all()
    user = User(
        email=str(payload.email),
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        is_superuser=payload.is_superuser,
        roles=list(roles),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permission("users.write"))],
)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = db.get(User, parse_request_id(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role_ids is not None:
        role_ids = parse_request_ids(payload.role_ids)
        user.roles = list(db.scalars(select(Role).where(Role.id.in_(role_ids))).all())
    db.commit()
    db.refresh(user)
    return user
