import uuid

from ums.domain.data_access.interfaces import Schema


class PermissionsCreate(Schema):
    name: str
    description: str | None


class PermissionsUpdate(Schema):
    id: uuid.UUID
    name: str
    description: str | None
    is_active: bool | None
