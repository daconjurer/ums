from typing import Sequence, Type
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Session, and_, select

from ums.crud.base import BaseRepository, CreateSchema, UpdateSchema
from ums.models import Permissions, RolePermissionLink


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

    def get_by_role_id(self, db: Session, role_id: UUID) -> Sequence[Permissions]:
        """Get permissions by role."""

        statement = (
            select(Permissions).join(
                RolePermissionLink,
                and_(
                    Permissions.id == RolePermissionLink.permission_id,
                    RolePermissionLink.role_id == str(role_id),
                ),
            )
            # Equivalent (but typed) to:
            # .join(RolePermissionLink, Permissions.id == RolePermissionLink.permission_id)
            # .filter(RolePermissionLink.role_id == role_id)
        )
        result = db.scalars(statement).all()
        return result


permissions_repository = PermissionsRepository()
