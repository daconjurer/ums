import sys
import uuid
from datetime import datetime
from typing import Type

from fastapi import Query
from pydantic import Field
from sqlalchemy.orm import selectinload
from sqlmodel import select

from ums.db.async_connection import AsyncDatabaseSession

if sys.version_info > (3, 11):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc

from ums.core import exceptions
from ums.crud.base import (
    BaseFilterParams,
    BaseRepository,
    CreateSchema,
    SortParams,
    UpdateSchema,
)
from ums.crud.group.validation import GroupValidator
from ums.models import Group, User


class GroupFilterParams(BaseFilterParams):
    name: str | None = Field(
        Query(default=None, examples=[""], description="Name of the group")
    )
    location: str | None = Field(
        Query(default=None, examples=[""], description="Location of the group")
    )
    description: str | None = Field(
        Query(default=None, examples=[""], description="Description of the group")
    )
    is_active: bool | None = Field(
        Query(default=None, examples=None, description="Whether the group is active")
    )
    is_deleted: bool | None = Field(
        Query(default=None, examples=None, description="Whether the group is deleted")
    )


class CrudGroup(BaseRepository[Group]):
    model: Type[Group] = Group
    filter_params: Type[GroupFilterParams] = GroupFilterParams

    async def add(
        self,
        db: AsyncDatabaseSession,
        input_object: CreateSchema,
    ) -> Group:
        """Create operation.

        Inserts a new Group record using the UserCreate schema.
        """
        await GroupValidator().validate(db, input_object)

        input_object_data = input_object.model_dump()

        if input_object_data.get("members_ids"):
            input_members_ids = set(input_object_data["members_ids"])
            statement = select(User).where(  # type: ignore
                User.is_active == True,  # noqa: E712
                User.id.in_(input_members_ids),  # type: ignore
            )

            async with db() as session:
                result = await session.scalars(statement)
                valid_users = result.all()
        else:
            valid_users = []

        db_obj = self.model(**input_object_data, members=valid_users)

        async with db() as session:
            session.add(db_obj)

        async with db() as session:
            db_obj = await session.merge(db_obj)

        return db_obj

    async def get(
        self,
        db: AsyncDatabaseSession,
        id: uuid.UUID,
    ) -> Group | None:
        """Read operation.

        Fetches a single Group record with the provided ID.
        """
        return await super().get(db, id)  # type: ignore

    async def get_by(
        self,
        db: AsyncDatabaseSession,
        filter: BaseFilterParams,
    ) -> Group | None:
        """Read operation.

        Fetches a Group record by a filter key-value pair.
        """
        return await super().get_by(db, filter)  # type: ignore

    async def get_many(  # type: ignore[override]
        self,
        db: AsyncDatabaseSession,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[Group]:
        """Read operation.

        Fetches a list of User records from the database with optional filtering,
         sorting and pagination.
        """
        return await super().get_many(db, filter, sort, limit, page)  # type: ignore

    async def update(
        self,
        db: AsyncDatabaseSession,
        obj_id: uuid.UUID,
        input_object: UpdateSchema,
    ) -> Group | None:
        """Update operation.

        Updates the record with the provided ID using the UpdateSchema schema.
        """
        await GroupValidator().validate(db, input_object)

        statement = (
            select(self.model)
            .options(selectinload(self.model.members))  # type: ignore
            .where(obj_id == self.model.id)
        )

        async with db() as session:
            db_obj = await session.scalar(statement)

            if not db_obj:
                raise exceptions.InvalidGroupException()

            # transform relationship fields to objects
            input_object_data = input_object.model_dump()

            if input_object_data.get("members_ids"):
                input_members_ids = set(input_object_data["members_ids"])
                statement = select(User).where(  # type: ignore
                    User.is_active == True,  # noqa: E712
                    User.id.in_(input_members_ids),  # type: ignore
                )

                result = await session.scalars(statement)
                valid_users = result.all()

                if valid_users:
                    db_obj.members = valid_users
            else:
                db_obj.members = []

            update_data = input_object.model_dump(exclude_unset=True)
            # Remove as it is now the members field
            del update_data["members_ids"]

            for key, value in update_data.items():
                setattr(db_obj, key, value)

            setattr(db_obj, "updated_at", datetime.now(tz=UTC))

            session.add(db_obj)

        async with db() as session:
            db_obj = await session.merge(db_obj)

        return db_obj

    async def delete(
        self,
        db: AsyncDatabaseSession,
        obj_id: uuid.UUID,
    ) -> Group | None:
        """Delete operation.

        Deletes the record with the provided ID.
        """
        return await super().delete(db, obj_id)  # type: ignore


group_repository = CrudGroup()
