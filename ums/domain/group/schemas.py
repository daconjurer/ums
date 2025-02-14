import uuid
from typing import Sequence

from ums.core.data_access.interfaces import Schema


class GroupCreate(Schema):
    name: str
    location: str
    description: str | None = None
    member_ids: Sequence[uuid.UUID] | None = None


class GroupUpdate(Schema):
    id: uuid.UUID
    name: str | None = None
    location: str | None = None
    description: str | None = None
    member_ids: Sequence[uuid.UUID] | None = None
    is_active: bool | None = None


class GroupPublic(Schema):
    name: str
    location: str
    description: str | None = None
