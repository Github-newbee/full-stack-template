from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field


SnowflakeId = Annotated[str, BeforeValidator(lambda value: str(value))]
Username = Annotated[str, Field(min_length=1, max_length=80)]
Password = Annotated[str, Field(min_length=8, max_length=128)]
FullName = Annotated[str, Field(max_length=120)]


class PermissionRead(BaseModel):
    code: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class RoleRead(BaseModel):
    id: SnowflakeId
    name: str
    description: str
    permissions: list[PermissionRead] = []

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    name: str
    description: str = ""
    permissions: list[str] = []


class UserRead(BaseModel):
    id: SnowflakeId
    username: Username
    email: EmailStr | None
    full_name: str
    is_active: bool
    is_superuser: bool
    roles: list[RoleRead] = []

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: Username
    email: EmailStr | None = None
    password: Password
    full_name: FullName = ""
    is_active: bool = True
    is_superuser: bool = False
    role_ids: list[SnowflakeId] = []


class UserUpdate(BaseModel):
    username: Username | None = None
    email: EmailStr | None = None
    password: Password | None = None
    full_name: FullName | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    role_ids: list[SnowflakeId] | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: Username
    password: str


class TaskRead(BaseModel):
    id: SnowflakeId
    name: str
    status: str
    progress: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    name: str
    message: str = ""


class AssetRead(BaseModel):
    id: SnowflakeId
    filename: str
    content_type: str
    size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
