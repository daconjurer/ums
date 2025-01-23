import asyncio
import uuid

# from fastapi import Query
from loguru import logger

# from pydantic import Field
# from ums.core.filter_sort import BaseFilterParams
from ums.db.async_session import get_async_session
from ums.domain.data_access.reader import GenericReader
from ums.domain.entities import User

# class UserFilterParams(BaseFilterParams):
#     name: str | None = Field(
#         Query(default=None, examples=[""], description="Name of the user"),
#     )
#     full_name: str | None = Field(
#         Query(default=None, examples=[""], description="Full name of the user"),
#     )
#     email: str | None = Field(
#         Query(default=None, examples=[""], description="Email of the user"),
#     )
#     is_active: bool | None = Field(
#         Query(default=None, examples=None, description="Whether the user is active"),
#     )
#     is_verified: bool | None = Field(
#         Query(default=None, examples=None, description="Whether the user is verified"),
#     )


# class UserSortOptions(SortOptions):
#     full_name = "full_name"
#     created_at = "created_at"
#     updated_at = "updated_at"


class UserReader(GenericReader[User]):
    model = User


user_reader = UserReader()
