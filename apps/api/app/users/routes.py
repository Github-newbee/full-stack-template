from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ServiceError, to_http_exception
from app.core.permissions import require_permission
from app.core.request_ids import parse_request_id, parse_request_ids
from app.core.security import CurrentUser
from app.models import User
from app.pagination import PageResponse
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users.service import UserService


router = APIRouter(prefix="/users", tags=["users"])


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
    result = UserService(db).list_users(page=page, page_size=page_size)
    return PageResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permission("users.read"))],
)
def get_user(user_id: str, db: Annotated[Session, Depends(get_db)]) -> User:
    try:
        return UserService(db).get_user(parse_request_id(user_id))
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.post(
    "",
    response_model=UserRead,
    dependencies=[Depends(require_permission("users.write"))],
)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser,
) -> User:
    role_ids = parse_request_ids(payload.role_ids)
    try:
        return UserService(db).create_user(payload, role_ids, actor=current_user)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permission("users.write"))],
)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser,
) -> User:
    parsed_role_ids = parse_request_ids(payload.role_ids) if payload.role_ids is not None else None
    try:
        return UserService(db).update_user(
            parse_request_id(user_id),
            payload,
            parsed_role_ids,
            actor=current_user,
        )
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("users.write"))],
)
def delete_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser,
) -> Response:
    try:
        UserService(db).delete_user(parse_request_id(user_id), actor=current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc
