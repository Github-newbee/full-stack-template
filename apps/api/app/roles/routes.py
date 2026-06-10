from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ServiceError, to_http_exception
from app.core.permissions import require_permission
from app.models import Role
from app.roles.service import RoleService
from app.schemas import PermissionRead, RoleCreate, RoleRead


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "",
    response_model=list[RoleRead],
    dependencies=[Depends(require_permission("roles.read"))],
)
def list_roles(db: Annotated[Session, Depends(get_db)]) -> list[Role]:
    return RoleService(db).list_roles()


@router.post(
    "",
    response_model=RoleRead,
    dependencies=[Depends(require_permission("roles.write"))],
)
def create_role(payload: RoleCreate, db: Annotated[Session, Depends(get_db)]) -> Role:
    try:
        return RoleService(db).create_role(payload)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.get(
    "/permissions",
    response_model=list[PermissionRead],
    dependencies=[Depends(require_permission("roles.read"))],
)
def list_permissions(db: Annotated[Session, Depends(get_db)]) -> list[PermissionRead]:
    return RoleService(db).list_permissions()
