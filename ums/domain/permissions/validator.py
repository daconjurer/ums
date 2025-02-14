from ums.core.db.async_session import AsyncSessionStream
from ums.domain.entities import Permissions
from ums.domain.permissions.schemas import PermissionsCreate, PermissionsUpdate


class PermissionsValidator:
    """Validates a PermissionsCreate or PermissionsUpdate object."""

    async def validate(
        self,
        db: AsyncSessionStream,
        input: PermissionsCreate | PermissionsUpdate,
    ) -> Permissions:
        # Attempt permissions instantiation
        valid_permissions = Permissions(
            **input.model_dump(exclude_none=True, exclude_unset=True),
        )

        return valid_permissions
