from typing import Sequence
from ums.models import Permissions
from ums.crud.permissions.repository import permissions_repository
from ums.db.session import get_session


def get_permissions_by_role_id(role_id: str) -> Sequence[Permissions]:
    """Get the permissions of a role."""
    permissions = permissions_repository.get_by_role_id(
        db=next(get_session()), role_id=role_id
    )
    return permissions
