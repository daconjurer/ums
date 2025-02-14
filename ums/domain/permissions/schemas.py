import uuid

from ums.core.data_access.interfaces import Schema


class PermissionsCreate(Schema):
    name: str
    description: str | None = None


class PermissionsUpdate(Schema):
    id: uuid.UUID
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
