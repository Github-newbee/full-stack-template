from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.core.permissions import PERMISSIONS
from app.models import Role
from app.roles.repository import RoleRepository
from app.schemas import PermissionRead, RoleCreate


class RoleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.roles = RoleRepository(db)

    def list_roles(self) -> list[Role]:
        return self.roles.list_roles()

    def create_role(self, payload: RoleCreate) -> Role:
        if self.roles.get_by_name(payload.name) is not None:
            raise ConflictError("Role already exists")

        permissions = self.roles.list_permissions_by_codes(payload.permissions)
        role = Role(name=payload.name, description=payload.description, permissions=permissions)
        self.roles.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def list_permissions(self) -> list[PermissionRead]:
        return [
            PermissionRead(code=code, description=description)
            for code, description in PERMISSIONS.items()
        ]
