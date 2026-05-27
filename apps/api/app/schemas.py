from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr


SnowflakeId = Annotated[str, BeforeValidator(lambda value: str(value))]


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
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    roles: list[RoleRead] = []

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    is_superuser: bool = False
    role_ids: list[SnowflakeId] = []


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
    role_ids: list[SnowflakeId] | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
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
