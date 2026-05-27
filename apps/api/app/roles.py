from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import PERMISSIONS
from app.core.security import get_password_hash
from app.models import Permission, Role, User


def seed_defaults(
    db: Session,
    *,
    admin_email: str = "admin@example.com",
    admin_password: str = "admin123456",
    admin_full_name: str = "Template Admin",
    seed_admin: bool = True,
) -> None:
    permissions_by_code: dict[str, Permission] = {}
    for code, description in PERMISSIONS.items():
        permission = db.scalars(select(Permission).where(Permission.code == code)).first()
        if permission is None:
            permission = Permission(code=code, description=description)
            db.add(permission)
        permissions_by_code[code] = permission

    admin_role = db.scalars(select(Role).where(Role.name == "admin")).first()
    if admin_role is None:
        admin_role = Role(name="admin", description="Full access")
        db.add(admin_role)
    admin_role.permissions = list(permissions_by_code.values())

    if seed_admin:
        admin_user = db.scalars(select(User).where(User.email == admin_email)).first()
        if admin_user is None:
            admin_user = User(
                email=admin_email,
                full_name=admin_full_name,
                hashed_password=get_password_hash(admin_password),
                is_superuser=True,
                roles=[admin_role],
            )
            db.add(admin_user)

    db.commit()
