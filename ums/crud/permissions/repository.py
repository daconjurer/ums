from typing import Type, Sequence
from pydantic import BaseModel
from sqlmodel import and_, Session, select

from ums.crud.base import BaseRepository, CreateSchema, UpdateSchema
from ums.models import Permissions, RolePermissionLink
from ums.middlewares.filter_sort import SortBy, FilterBy, SortOptions


class PermissionsCreate(CreateSchema):
    name: str
    description: str | None


class PermissionsUpdate(UpdateSchema):
    name: str
    description: str | None
    is_active: bool | None


class PermissionsPublic(BaseModel):
    name: str
    description: str | None


class PermissionsRepository(BaseRepository):
    model: Type[Permissions] = Permissions

    def get_by_role_id(self, db: Session, role_id: str) -> Sequence[Permissions]:
        """Get permissions by role."""

        statement = (
            select(Permissions).join(
                RolePermissionLink,
                and_(
                    Permissions.id == RolePermissionLink.permission_id,
                    RolePermissionLink.role_id == role_id,
                ),
            )
            # Equivalent (but typed) to:
            # .join(RolePermissionLink, Permissions.id == RolePermissionLink.permission_id)
            # .filter(RolePermissionLink.role_id == role_id)
        )
        result = db.scalars(statement).all()
        return result


permissions_repository = PermissionsRepository()
