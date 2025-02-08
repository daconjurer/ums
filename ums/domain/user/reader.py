from pydantic import Field

from ums.core.filter_sort import BaseFilterParams
from ums.data_access.reader import GenericReader
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


class UserReader(GenericReader[User]):
    model = User


user_reader = UserReader()
