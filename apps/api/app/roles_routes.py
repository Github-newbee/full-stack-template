from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import PERMISSIONS, require_permission
from app.models import Permission, Role
from app.schemas import PermissionRead, RoleCreate, RoleRead


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "",
    response_model=list[RoleRead],
    dependencies=[Depends(require_permission("roles.read"))],
)
def list_roles(db: Annotated[Session, Depends(get_db)]) -> list[Role]:
    return list(db.scalars(select(Role).order_by(Role.id)).all())


@router.post(
    "",
    response_model=RoleRead,
    dependencies=[Depends(require_permission("roles.write"))],
)
def create_role(payload: RoleCreate, db: Annotated[Session, Depends(get_db)]) -> Role:
    existing = db.scalars(select(Role).where(Role.name == payload.name)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Role already exists")
    permissions = db.scalars(select(Permission).where(Permission.code.in_(payload.permissions))).all()
    role = Role(name=payload.name, description=payload.description, permissions=list(permissions))
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get(
    "/permissions",
    response_model=list[PermissionRead],
    dependencies=[Depends(require_permission("roles.read"))],
)
def list_permissions() -> list[PermissionRead]:
    return [PermissionRead(code=code, description=description) for code, description in PERMISSIONS.items()]
