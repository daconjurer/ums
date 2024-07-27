import uuid
from typing import Sequence

from ums.crud.base import CreateSchema, UpdateSchema


class GroupCreate(CreateSchema):
    name: str
    location: str
    description: str | None
    members_ids: Sequence[uuid.UUID] | None


class GroupUpdate(UpdateSchema):
    name: str
    location: str | None
    description: str | None
    members_ids: Sequence[uuid.UUID] | None
    is_active: bool | None
