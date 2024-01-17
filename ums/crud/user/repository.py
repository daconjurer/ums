from typing import Type, Any
from sqlmodel import Session
import uuid
from enum import Enum
from datetime import datetime

from ums.core.security import get_password_hash
from ums.crud.base import BaseRepository, CreateSchema, UpdateSchema
from ums.crud.user.validation import UserValidator
from ums.models import User
from ums.core import exceptions
from ums.middlewares.filter_sort import FilterBy, SortBy


class UserFilterByEnum(str, Enum):
    name = "name"
    full_name = "full_name"
    email = "email"
    is_active = "is_active"
    is_verified = "is_verified"
    is_deleted = "is_deleted"


class UserSortByEnum(str, Enum):
    name = "name"
    created_at = "created_at"
    updated_at = "upated_at"


class UserRepository(BaseRepository[User]):
    model: Type[User] = User

    _filter_to_column: dict[str, Any] = {
        UserFilterByEnum.name: model.name,
        UserFilterByEnum.full_name: model.full_name,
        UserFilterByEnum.email: model.email,
        UserFilterByEnum.is_deleted: model.is_deleted,
        UserFilterByEnum.is_active: model.is_active,
        UserFilterByEnum.is_verified: model.is_verified,
    }

    _sort_to_column: dict[str, Any] = {
        UserSortByEnum.name: model.name,
        UserSortByEnum.created_at: model.created_at,
        UserSortByEnum.updated_at: model.updated_at,
    }

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
        filter: FilterBy,
    ) -> User | None:
        """Read operation.

        Fetches a User record by a filter key-value pair.
        """
        return super().get_by(db, filter)  # type: ignore

    def get_many(  # type: ignore[override]
        self,
        db: Session,
        filter: list[FilterBy] | None = None,
        sort: SortBy | None = None,
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

        update_datetime = datetime.utcnow()

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
