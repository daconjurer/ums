from typing import Sequence
from uuid import UUID

from sqlmodel import and_, select

from ums.core.service.domain import DomainService
from ums.domain.entities import Permissions, RolePermissionLink
from ums.domain.permissions.reader import permissions_reader
from ums.domain.permissions.schemas import PermissionsCreate
from ums.domain.permissions.validator import PermissionsValidator
from ums.domain.permissions.writer import permissions_writer


class PermissionsService(DomainService[Permissions]):
    reader = permissions_reader
    writer = permissions_writer

    async def add_permissions(
        self,
        permissions_create: PermissionsCreate,
    ) -> Permissions:
        # Validate permissions
        validated_permissions = await PermissionsValidator().validate(
            self.db, permissions_create
        )

        # Create record
        async with self.db() as session:
            permissions = await permissions_writer.create(
                session, validated_permissions
            )
            await session.commit()
            return permissions

    async def get_by_role_id(
        self,
        role_id: UUID,
    ) -> Sequence[Permissions]:
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
            # select(Permissions)
            # .join(RolePermissionLink, Permissions.id == RolePermissionLink.permission_id)
            # .filter(RolePermissionLink.role_id == role_id)
        )
        async with self.db() as session:
            entities = await session.scalars(statement)
            result = list(entities.all())

        return result
