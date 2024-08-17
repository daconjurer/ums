from typing import Sequence
from uuid import UUID

from fastapi import Depends
from typing_extensions import Annotated

from ums.crud.permissions.repository import permissions_repository
from ums.db.session import Session, get_session
from ums.models import Permissions


def get_permissions_by_role_id(
    role_id: UUID,
    db: Annotated[Session, Depends(get_session)],
) -> Sequence[Permissions]:
    """Get the permissions of a role."""
    permissions = permissions_repository.get_by_role_id(db=db, role_id=role_id)
    return permissions
