import uuid
from typing import Sequence

from pydantic import EmailStr

from ums.core.data_access.interfaces import Schema


class UserCreate(Schema):
    name: str
    full_name: str
    email: EmailStr
    password: str
    role_id: uuid.UUID | None = None
    group_ids: Sequence[uuid.UUID] | None = None


class UserUpdate(Schema):
    id: uuid.UUID
    name: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role_id: uuid.UUID | None = None
    group_ids: Sequence[uuid.UUID] | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserPublic(Schema):
    name: str
    full_name: str
    email: EmailStr
    is_verified: bool
