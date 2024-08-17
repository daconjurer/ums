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
from ums.core.security import get_password_hash
from ums.crud.base import (
    BaseFilterParams,
    BaseRepository,
    CreateSchema,
    SortParams,
    UpdateSchema,
)
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


# UserSortOptions = Literal["full_name", "created_at", "updated_at"]
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

    def add(self, db: Session, input_object: CreateSchema) -> User:
        """Create operation.

        Inserts a new User record using the UserCreate schema.
        """
        validated_user = UserValidator().validate(db, input_object)

        # Hash password
        validated_user["password"] = get_password_hash(validated_user["password"])

        de_obj = self.model(**validated_user)
        db.add(de_obj)
        db.commit()
        db.refresh(de_obj)
        return de_obj  # type: ignore

    def get(self, db: Session, id: uuid.UUID) -> User | None:
        """Read operation.

        Fetches a single User record with the provided ID.
        """
        return super().get(db, id)  # type: ignore

    def get_by(
        self,
        db: Session,
        filter: BaseFilterParams,
    ) -> User | None:
        """Read operation.

        Fetches a User record by a filter key-value pair.
        """
        return super().get_by(db, filter)  # type: ignore

    def get_many(  # type: ignore[override]
        self,
        db: Session,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[User]:  # type: ignore
        """Read operation.

        Fetches a list of User records from the database with optional filtering,
         sorting and pagination.
        """
        return super().get_many(db, filter, sort, limit, page)  # type: ignore

    def update(
        self, db: Session, obj_id: uuid.UUID, input_object: UpdateSchema
    ) -> User:
        """Update operation.

        Updates the record with the provided ID using the UpdateSchema schema.
        """
        db_obj = self.get(db, obj_id)

        if not db_obj:
            raise exceptions.InvalidUserException()

        validated_user = UserValidator().validate(db, input_object)

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

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj  # type: ignore

    def delete(self, db: Session, obj_id: uuid.UUID) -> User | None:
        """Delete operation.

        Deletes the record with the provided ID.
        """
        return super().delete(db, obj_id)  # type: ignore


user_repository = UserRepository()
