from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.service import AuthService
from app.core.database import get_db
from app.core.errors import ServiceError, to_http_exception
from app.core.security import CurrentUser
from app.schemas import LoginRequest, Token, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    try:
        access_token = AuthService(db).login(username=payload.username, password=payload.password)
        return Token(access_token=access_token)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> CurrentUser:
    return current_user
