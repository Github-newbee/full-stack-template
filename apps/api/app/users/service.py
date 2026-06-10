from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.core.security import get_password_hash
from app.models import Role, User
from app.pagination import PageResult
from app.roles.repository import RoleRepository
from app.schemas import UserCreate, UserUpdate
from app.users.repository import UserRepository


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)

    def list_users(self, *, page: int, page_size: int) -> PageResult[User]:
        total = self.users.count()
        users = self.users.list_page(offset=(page - 1) * page_size, limit=page_size)
        return PageResult(items=users, total=total, page=page, page_size=page_size)

    def get_user(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    def create_user(self, payload: UserCreate, role_ids: list[int], *, actor: User) -> User:
        if payload.is_superuser and not actor.is_superuser:
            raise ForbiddenError("Only superusers can create superusers")
        if self.users.get_by_username(payload.username) is not None:
            raise ConflictError("用户名已存在，请更换后重试")
        if payload.email is not None and self.users.get_by_email(str(payload.email)) is not None:
            raise ConflictError("邮箱已存在，请更换后重试")

        user = User(
            username=payload.username,
            email=str(payload.email) if payload.email is not None else None,
            full_name=payload.full_name,
            hashed_password=get_password_hash(payload.password),
            is_active=payload.is_active,
            is_superuser=payload.is_superuser,
            roles=self._get_roles(role_ids),
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(
        self,
        user_id: int,
        payload: UserUpdate,
        role_ids: list[int] | None,
        *,
        actor: User,
    ) -> User:
        user = self.get_user(user_id)
        self._ensure_can_manage(user, actor)

        if user.id == actor.id and payload.is_active is False:
            raise ConflictError("You cannot deactivate your own account")
        if user.id == actor.id and payload.is_superuser is False and user.is_superuser:
            raise ConflictError("You cannot remove your own superuser status")
        if payload.is_superuser is not None and payload.is_superuser != user.is_superuser:
            if not actor.is_superuser:
                raise ForbiddenError("Only superusers can change superuser status")
            if user.is_superuser and not payload.is_superuser:
                self._ensure_another_active_superuser(user)
        if payload.is_active is False and user.is_active and user.is_superuser:
            self._ensure_another_active_superuser(user)

        if payload.username is not None and payload.username != user.username:
            existing = self.users.get_by_username(payload.username)
            if existing is not None:
                raise ConflictError("用户名已存在，请更换后重试")
            user.username = payload.username
        if "email" in payload.model_fields_set and payload.email != user.email:
            if payload.email is not None:
                existing = self.users.get_by_email(str(payload.email))
                if existing is not None:
                    raise ConflictError("邮箱已存在，请更换后重试")
            user.email = str(payload.email) if payload.email is not None else None
        if payload.password is not None:
            user.hashed_password = get_password_hash(payload.password)
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.is_superuser is not None:
            user.is_superuser = payload.is_superuser
        if role_ids is not None:
            user.roles = self._get_roles(role_ids)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int, *, actor: User) -> None:
        user = self.get_user(user_id)
        self._ensure_can_manage(user, actor)
        if user.id == actor.id:
            raise ConflictError("You cannot delete your own account")
        if user.is_active and user.is_superuser:
            self._ensure_another_active_superuser(user)

        self.users.delete(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("User is referenced by other records") from exc

    def _get_roles(self, role_ids: list[int]) -> list[Role]:
        unique_role_ids = list(dict.fromkeys(role_ids))
        roles = self.roles.list_by_ids(unique_role_ids)
        if len(roles) != len(unique_role_ids):
            raise NotFoundError("Role not found")
        return roles

    def _ensure_can_manage(self, user: User, actor: User) -> None:
        if user.is_superuser and not actor.is_superuser:
            raise ForbiddenError("Only superusers can manage superusers")

    def _ensure_another_active_superuser(self, user: User) -> None:
        if user.is_active and user.is_superuser and self.users.count_active_superusers() <= 1:
            raise ConflictError("At least one active superuser is required")
