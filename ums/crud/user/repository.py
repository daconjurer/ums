import sys
import uuid
from datetime import datetime
from typing import Type

from fastapi import Query
from pydantic import Field
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ums.db.async_connection import AsyncDatabaseSession

if sys.version_info > (3, 11):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc

from ums.core import exceptions
from ums.core.security import get_password_hash
from ums.crud.base import (
    BaseFilterParams,
    BaseRepository,
    CreateSchema,
    SortParams,
    UpdateSchema,
)
from ums.crud.user.schemas import UserCreate
from ums.crud.user.validation import UserValidator
from ums.middlewares.filter_sort import SortOptions
from ums.models import User


class UserFilterParams(BaseFilterParams):
    name: str | None = Field(
        Query(default=None, examples=[""], description="Name of the user"),
    )
    full_name: str | None = Field(
        Query(default=None, examples=[""], description="Full name of the user"),
    )
    email: str | None = Field(
        Query(default=None, examples=[""], description="Email of the user"),
    )
    is_active: bool | None = Field(
        Query(default=None, examples=None, description="Whether the user is active"),
    )
    is_verified: bool | None = Field(
        Query(default=None, examples=None, description="Whether the user is verified"),
    )


class UserSortOptions(SortOptions):
    full_name = "full_name"
    created_at = "created_at"
    updated_at = "updated_at"


class UserRepository(BaseRepository[User]):
    model: Type[User] = User
    filter_params: Type[UserFilterParams] = UserFilterParams
    sort_options: tuple[str, ...] | None = tuple(
        member.value for member in UserSortOptions
    )

    async def add(self, db: AsyncDatabaseSession, input_object: CreateSchema) -> User:
        """Create operation.

        Inserts a new User record using the UserCreate schema.
        """
        validated_user = await UserValidator().validate(db, input_object)

        # Hash password
        validated_user["password"] = get_password_hash(validated_user["password"])

        # Create object
        validated_object = UserCreate(**validated_user)
        return await super().add(db, validated_object)  # type: ignore

    async def get(self, db: AsyncDatabaseSession, id: uuid.UUID) -> User | None:
        """Read operation.

        Fetches a single User record with the provided ID.
        """
        statement = (
            select(self.model)
            .options(joinedload(self.model.groups))  # type: ignore
            .where(id == self.model.id)
        )

        async with db() as session:
            result = await session.scalar(statement)

        return result

    async def get_by(
        self,
        db: AsyncDatabaseSession,
        filter: BaseFilterParams,
    ) -> User | None:
        """Read operation.

        Fetches a User record by a filter key-value pair.
        """
        return await super().get_by(db, filter)  # type: ignore

    async def get_many(  # type: ignore[override]
        self,
        db: AsyncDatabaseSession,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[User]:  # type: ignore
        """Read operation.

        Fetches a list of User records from the database with optional filtering,
         sorting and pagination.
        """
        return await super().get_many(db, filter, sort, limit, page)  # type: ignore

    async def update(
        self, db: AsyncDatabaseSession, obj_id: uuid.UUID, input_object: UpdateSchema
    ) -> User | None:
        """Update operation.

        Updates the record with the provided ID using the UpdateSchema schema.
        """
        db_obj = await self.get(db, obj_id)

        if not db_obj:
            raise exceptions.InvalidUserException()

        validated_user = await UserValidator().validate(db, input_object)

        # Password update
        if validated_user.get("password"):
            validated_user["password"] = get_password_hash(validated_user["password"])

        update_datetime = datetime.now(tz=UTC)

        for key, value in validated_user.items():
            setattr(db_obj, key, value)

        # Verification datetime update
        if validated_user.get("is_verified"):
            setattr(db_obj, "verified_at", update_datetime)

        setattr(db_obj, "updated_at", update_datetime)

        async with db() as session:
            session.add(db_obj)
            db_obj = await session.merge(db_obj)

        return db_obj

    async def delete(self, db: AsyncDatabaseSession, obj_id: uuid.UUID) -> User | None:
        """Delete operation.

        Deletes the record with the provided ID.
        """
        return await super().delete(db, obj_id)  # type: ignore


user_repository = UserRepository()
