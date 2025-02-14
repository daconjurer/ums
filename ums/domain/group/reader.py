from pydantic import Field

from ums.core.data_access.reader import GenericReader
from ums.core.utils.filter_sort import BaseFilterParams
from ums.domain.entities import Group


class GroupFilterParams(BaseFilterParams):
    name: str | None = Field(
        default=None,
        examples=[""],
        description="Name of the group",
    )
    location: str | None = Field(
        default=None,
        examples=[""],
        description="Location of the group",
    )
    is_active: bool | None = Field(
        default=None,
        examples=None,
        description="Whether the group is active",
    )
    is_deleted: bool | None = Field(
        default=None,
        examples=None,
        description="Whether the group is deleted",
    )


class GroupReader(GenericReader[Group]):
    model = Group


group_reader = GroupReader()
