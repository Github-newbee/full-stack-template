from collections.abc import Callable

from fastapi import HTTPException, status

from app.core.security import CurrentUser


PERMISSIONS = {
    "admin": "System administration",
    "users.read": "Read users",
    "users.write": "Create and update users",
    "roles.read": "Read roles",
    "roles.write": "Create and update roles",
    "tasks.read": "Read tasks",
    "tasks.write": "Create and update tasks",
    "assets.read": "Read assets",
    "assets.write": "Upload assets",
}


def require_permission(permission: str) -> Callable[[CurrentUser], CurrentUser]:
    def dependency(current_user: CurrentUser) -> CurrentUser:
        if current_user.is_superuser:
            return current_user
        permissions = {item.code for role in current_user.roles for item in role.permissions}
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency
