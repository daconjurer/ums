from typing import Type
from pydantic import BaseModel
from ums.crud.base import BaseRepository, CreateSchema, UpdateSchema
from ums.models import Role, Permissions

from sqlmodel import SQLModel


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
