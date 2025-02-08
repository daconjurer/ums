from typing import Sequence
from uuid import UUID

from sqlmodel import and_, select

from ums.domain.entities import Permissions, RolePermissionLink
from ums.domain.permissions.reader import permissions_reader
from ums.domain.permissions.writer import permissions_writer
from ums.domain.service.domain import DomainService


class PermissionsService(DomainService[Permissions]):
    reader = permissions_reader
    writer = permissions_writer

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
            # .join(RolePermissionLink, Permissions.id == RolePermissionLink.permission_id)
            # .filter(RolePermissionLink.role_id == role_id)
        )
        async with self.db() as session:
            entities = await session.scalars(statement)
            result = list(entities.all())

        return result
