from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends

from ums.crud.permissions.repository import permissions_repository
from ums.db.async_connection import AsyncDatabaseSession, db
from ums.domain.entities import Permissions


async def get_permissions_by_role_id(
    role_id: UUID,
    db: Annotated[AsyncDatabaseSession, Depends(db)],
) -> Sequence[Permissions]:
    """Get the permissions of a role."""
    permissions = await permissions_repository.get_by_role_id(db=db, role_id=role_id)
    return permissions
