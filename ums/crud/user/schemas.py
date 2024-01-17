from typing import Sequence
from pydantic import EmailStr
import uuid
from ums.crud.base import CreateSchema, UpdateSchema


class UserCreate(CreateSchema):
    name: str
    full_name: str
    email: EmailStr
    password: str
    role_id: uuid.UUID | None = None
    groups_ids: Sequence[uuid.UUID] | None = None


class UserUpdate(UpdateSchema):
    name: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role_id: uuid.UUID | None = None
    groups_ids: Sequence[uuid.UUID] | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
