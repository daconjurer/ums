from typing import Sequence
from uuid import UUID

from ums.crud.permissions.repository import permissions_repository
from ums.db.session import get_session
from ums.models import Permissions


def get_permissions_by_role_id(role_id: UUID) -> Sequence[Permissions]:
    """Get the permissions of a role."""
    permissions = permissions_repository.get_by_role_id(
        db=next(get_session()), role_id=role_id
    )
    return permissions
