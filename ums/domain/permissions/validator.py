from sqlmodel import select

from ums.db.async_session import AsyncSessionStream
from ums.domain import exceptions
from ums.domain.entities import Permissions, Role
from ums.domain.permissions.schemas import PermissionsCreate, PermissionsUpdate


class PermissionsValidator:
    """Validates a PermissionsCreate or PermissionsUpdate object."""

    async def validate(
        self,
        db: AsyncSessionStream,
        input: PermissionsCreate | PermissionsUpdate,
    ) -> Permissions:
        # Check role IDs are valid
        permissions_roles = []
        if input.role_ids:
            statement = select(Role).where(Role.is_active == True)  # type: ignore  # noqa: E712

            async with db() as session:
                result = await session.scalars(statement)
                await session.commit()
                active_roles = result.all()

            if active_roles:
                active_role_ids_set = {role.id for role in active_roles}
                input_role_ids_set = set(input.role_ids)

                invalid_role_ids = input_role_ids_set - active_role_ids_set

                if invalid_role_ids:
                    raise exceptions.InvalidRoleException(
                        f"Invalid role_id: {invalid_role_ids.pop()}"
                    )

                permissions_roles = [
                    role for role in active_roles if role.id in input_role_ids_set
                ]

        # Assign roles
        valid_permissions = Permissions(
            **input.model_dump(exclude_none=True, exclude_unset=True),
            roles=permissions_roles,
        )

        return valid_permissions
