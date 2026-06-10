import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.core.security import get_password_hash, verify_password
from app.models import Base, Role, User
from app.schemas import UserCreate, UserUpdate
from app.users.service import UserService


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def add_user(
    db: Session,
    *,
    username: str,
    email: str,
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    user = User(
        username=username,
        email=email,
        full_name="",
        hashed_password=get_password_hash("password123"),
        is_active=is_active,
        is_superuser=is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_user_service_crud(db: Session) -> None:
    actor = add_user(
        db,
        username="admin",
        email="admin@example.com",
        is_superuser=True,
    )
    role = Role(name="operator", description="Operator")
    db.add(role)
    db.commit()
    db.refresh(role)

    service = UserService(db)
    created = service.create_user(
        UserCreate(
            username="alice",
            email="alice@example.com",
            password="password123",
            full_name="Alice",
            role_ids=[str(role.id)],
        ),
        [role.id],
        actor=actor,
    )

    assert service.get_user(created.id).username == "alice"
    assert [item.id for item in created.roles] == [role.id]

    updated = service.update_user(
        created.id,
        UserUpdate(
            username="alice-updated",
            email="alice-updated@example.com",
            password="new-password123",
            full_name="Alice Updated",
            is_active=False,
            role_ids=[],
        ),
        [],
        actor=actor,
    )

    assert updated.username == "alice-updated"
    assert updated.email == "alice-updated@example.com"
    assert updated.full_name == "Alice Updated"
    assert updated.is_active is False
    assert updated.roles == []
    assert verify_password("new-password123", updated.hashed_password)

    service.delete_user(updated.id, actor=actor)
    with pytest.raises(NotFoundError):
        service.get_user(updated.id)


def test_user_service_allows_missing_and_cleared_email(db: Session) -> None:
    actor = add_user(
        db,
        username="admin",
        email="admin@example.com",
        is_superuser=True,
    )
    service = UserService(db)

    created = service.create_user(
        UserCreate(
            username="alice",
            password="password123",
        ),
        [],
        actor=actor,
    )

    assert created.email is None

    with_email = service.update_user(
        created.id,
        UserUpdate(email="alice@example.com"),
        None,
        actor=actor,
    )

    assert with_email.email == "alice@example.com"

    updated = service.update_user(created.id, UserUpdate(email=None), None, actor=actor)

    assert updated.email is None


def test_user_service_returns_friendly_duplicate_username_message(db: Session) -> None:
    actor = add_user(
        db,
        username="admin",
        email="admin@example.com",
        is_superuser=True,
    )
    add_user(db, username="alice", email="alice@example.com")

    with pytest.raises(ConflictError, match="用户名已存在"):
        UserService(db).create_user(
            UserCreate(
                username="alice",
                password="password123",
            ),
            [],
            actor=actor,
        )


def test_user_service_rejects_unknown_roles(db: Session) -> None:
    actor = add_user(
        db,
        username="admin",
        email="admin@example.com",
        is_superuser=True,
    )

    with pytest.raises(NotFoundError, match="Role not found"):
        UserService(db).create_user(
            UserCreate(
                username="alice",
                email="alice@example.com",
                password="password123",
                role_ids=["123"],
            ),
            [123],
            actor=actor,
        )


def test_regular_user_cannot_manage_superusers(db: Session) -> None:
    actor = add_user(db, username="operator", email="operator@example.com")
    superuser = add_user(
        db,
        username="admin",
        email="admin@example.com",
        is_superuser=True,
    )
    service = UserService(db)

    with pytest.raises(ForbiddenError):
        service.create_user(
            UserCreate(
                username="second-admin",
                email="second-admin@example.com",
                password="password123",
                is_superuser=True,
            ),
            [],
            actor=actor,
        )

    with pytest.raises(ForbiddenError):
        service.update_user(
            superuser.id,
            UserUpdate(full_name="Changed"),
            None,
            actor=actor,
        )


def test_cannot_remove_current_or_last_active_superuser(db: Session) -> None:
    actor = add_user(
        db,
        username="admin",
        email="admin@example.com",
        is_superuser=True,
    )
    service = UserService(db)

    with pytest.raises(ConflictError, match="deactivate your own"):
        service.update_user(actor.id, UserUpdate(is_active=False), None, actor=actor)

    with pytest.raises(ConflictError, match="delete your own"):
        service.delete_user(actor.id, actor=actor)

    second_superuser = add_user(
        db,
        username="second-admin",
        email="second-admin@example.com",
        is_superuser=True,
    )
    actor.is_active = False
    db.commit()
    with pytest.raises(ConflictError, match="At least one active superuser"):
        service.update_user(
            second_superuser.id,
            UserUpdate(is_active=False),
            None,
            actor=actor,
        )
