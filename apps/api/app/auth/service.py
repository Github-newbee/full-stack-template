from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.users.repository import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def login(self, *, username: str, password: str) -> str:
        user = self.users.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect username or password")
        return create_access_token(str(user.id))
