import uuid
from typing import Sequence

from ums.crud.base import CreateSchema, UpdateSchema


class GroupCreate(CreateSchema):
    name: str
    location: str
    description: str | None = None
    members_ids: Sequence[uuid.UUID] | None = None


class GroupUpdate(UpdateSchema):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    members_ids: Sequence[uuid.UUID] | None = None
    is_active: bool | None = None
