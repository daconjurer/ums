from pydantic import Field

from ums.core.filter_sort import BaseFilterParams, FilterMapper, SortMapper, SortOptions
from ums.domain.data_access.reader import GenericReader
from ums.domain.entities import User


class UserFilterParams(BaseFilterParams):
    name: str | None = Field(
        default=None,
        examples=[""],
        description="Name of the user",
    )
    full_name: str | None = Field(
        default=None,
        examples=[""],
        description="Full name of the user",
    )
    email: str | None = Field(
        default=None,
        examples=[""],
        description="Email of the user",
    )
    is_active: bool | None = Field(
        default=None,
        examples=None,
        description="Whether the user is active",
    )
    is_verified: bool | None = Field(
        default=None,
        examples=None,
        description="Whether the user is verified",
    )


class UserSortOptions(SortOptions):
    full_name = "full_name"
    created_at = "created_at"
    updated_at = "updated_at"


class UserReader(GenericReader[User]):
    model = User
    filter_mapper = FilterMapper()
    sort_mapper = SortMapper(UserSortOptions)


user_reader = UserReader()
