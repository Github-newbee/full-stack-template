from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(User)) or 0

    def list_page(self, *, offset: int, limit: int) -> list[User]:
        return list(
            self.db.scalars(select(User).order_by(User.id).offset(offset).limit(limit)).all()
        )

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalars(select(User).where(User.username == username)).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalars(select(User).where(User.email == email)).first()

    def count_active_superusers(self) -> int:
        return (
            self.db.scalar(
                select(func.count())
                .select_from(User)
                .where(User.is_superuser.is_(True), User.is_active.is_(True))
            )
            or 0
        )

    def add(self, user: User) -> None:
        self.db.add(user)

    def delete(self, user: User) -> None:
        self.db.delete(user)
