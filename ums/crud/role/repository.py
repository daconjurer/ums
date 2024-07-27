from typing import Type

from pydantic import BaseModel
from sqlmodel import SQLModel

from ums.crud.base import BaseRepository, CreateSchema, UpdateSchema
from ums.models import Permissions, Role


class RoleCreate(CreateSchema):
    name: str
    description: str | None


class RoleUpdate(UpdateSchema):
    name: str
    description: str | None
    is_active: bool | None


class RolePublic(BaseModel):
    name: str
    description: str | None
    permissions: list[Permissions]


class RoleRepository(BaseRepository):
    model: Type[SQLModel] = Role


role_repository = RoleRepository()
