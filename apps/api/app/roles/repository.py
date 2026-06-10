from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Permission, Role


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_roles(self) -> list[Role]:
        return list(self.db.scalars(select(Role).order_by(Role.id)).all())

    def get_by_name(self, name: str) -> Role | None:
        return self.db.scalars(select(Role).where(Role.name == name)).first()

    def list_by_ids(self, role_ids: list[int]) -> list[Role]:
        if not role_ids:
            return []
        return list(self.db.scalars(select(Role).where(Role.id.in_(role_ids))).all())

    def list_permissions_by_codes(self, codes: list[str]) -> list[Permission]:
        if not codes:
            return []
        return list(self.db.scalars(select(Permission).where(Permission.code.in_(codes))).all())

    def add(self, role: Role) -> None:
        self.db.add(role)
