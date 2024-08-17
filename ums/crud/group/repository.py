import sys
import uuid
from datetime import datetime
from typing import Type

from fastapi import Query
from pydantic import Field
from sqlmodel import Session

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
from ums.models import Group


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

    def add(self, db: Session, input_object: CreateSchema) -> Group:
        """Create operation.

        Inserts a new Group record using the UserCreate schema.
        """
        validated_group = GroupValidator().validate(db, input_object)

        db_obj = self.model(**validated_group)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj  # type: ignore

    def get(self, db: Session, id: uuid.UUID) -> Group | None:
        """Read operation.

        Fetches a single Group record with the provided ID.
        """
        return super().get(db, id)  # type: ignore

    def get_by(
        self,
        db: Session,
        filter: BaseFilterParams,
    ) -> Group | None:
        """Read operation.

        Fetches a Group record by a filter key-value pair.
        """
        return super().get_by(db, filter)  # type: ignore

    def get_many(  # type: ignore[override]
        self,
        db: Session,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[Group]:
        """Read operation.

        Fetches a list of User records from the database with optional filtering,
         sorting and pagination.
        """
        return super().get_many(db, filter, sort, limit, page)  # type: ignore

    def update(
        self, db: Session, obj_id: uuid.UUID, input_object: UpdateSchema
    ) -> Group:
        """Update operation.

        Updates the record with the provided ID using the UpdateSchema schema.
        """
        db_obj = self.get(db, obj_id)

        if not db_obj:
            raise exceptions.InvalidGroupException()

        validated_group = GroupValidator().validate(db, input_object)

        for key, value in validated_group.items():
            setattr(db_obj, key, value)

        setattr(db_obj, "updated_at", datetime.now(tz=UTC))

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj  # type: ignore

    def delete(self, db: Session, obj_id: uuid.UUID) -> Group | None:
        """Delete operation.

        Deletes the record with the provided ID.
        """
        return super().delete(db, obj_id)  # type: ignore


group_repository = CrudGroup()
