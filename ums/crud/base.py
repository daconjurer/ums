"""Base CRUD module.

Provides the base functionality for typical CRUD operations.
"""
from typing import Type, Generic, TypeVar, Any
from pydantic import BaseModel
import uuid
from loguru import logger
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select, SQLModel
from ums.models import Base
from ums.middlewares.filter_sort import SortBy, FilterBy, SortOptions
from ums.core.exceptions import UMSException


ModelType = TypeVar("ModelType", bound=Base)


class CreateSchema(SQLModel):
    ...


class UpdateSchema(SQLModel):
    ...


class BaseRepository(BaseModel, Generic[ModelType]):
    """CRUD object with default methods."""

    model: Type[ModelType]
    _filter_to_column: dict[str, Any] = {}
    _sort_to_column: dict[str, Any] = {}

    def add(
        self,
        db: Session,
        input_object: CreateSchema,
    ) -> Base:
        """Create operation.

        Inserts a new record using the CreateSchema schema.
        """
        input_object_data = jsonable_encoder(input_object)
        db_obj = self.model(**input_object_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: uuid.UUID) -> Base | None:
        """Read operation.

        Fetches a single record with the provided ID.
        """
        statement = select(self.model).where(id == self.model.id)  # type: ignore
        result = db.scalar(statement)
        return result

    def get_by(
        self,
        db: Session,
        filter: FilterBy,
    ) -> Base | None:
        """Read operation.

        Fetches a record by a filter key-value pair.
        """
        filter_field = self._filter_to_column.get(filter.key, None)
        if filter_field:
            statement = select(self.model).where(filter_field == filter.value)
            return db.scalar(statement)
        return None

    def get_many(
        self,
        db: Session,
        filter: list[FilterBy] | None = None,
        sort: SortBy | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[Base]:
        """Read operation.

        Fetches a list of records from the database with optional filtering,
         sorting and pagination.
        """
        statement = select(self.model)

        # Apply filtering
        if filter:
            for f in filter:
                filter_field = self._filter_to_column.get(f.key, None)
                if filter_field:
                    statement = statement.where(filter_field == f.value)

        # Apply sorting
        if sort:
            if sort.by:
                column_to_sort = self._sort_to_column.get(sort.key, None)
                if column_to_sort:
                    statement = statement.order_by(
                        column_to_sort.asc()
                        if sort.by == SortOptions.asc
                        else column_to_sort.desc()
                    )

        # Apply pagination
        if page is not None and limit is not None:
            page = 1 if page < 1 else page
            offset = (page - 1) * limit
            statement = statement.offset(offset).limit(limit)

        # Query
        logger.debug(statement.compile(compile_kwargs={"literal_binds": True}))
        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        obj_id: uuid.UUID,
        input_object: UpdateSchema,
    ) -> Base:
        """Update operation.

        Updates the record with the provided ID using the UpdateSchema schema.
        """
        db_obj = self.get(db, obj_id)

        if not db_obj:
            raise UMSException(status_code=404, detail="Object not found.")

        update_data = input_object.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_obj, key, value)

        setattr(db_obj, "updated_at", datetime.utcnow())

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, obj_id: uuid.UUID) -> Base | None:
        """Delete operation.

        Deletes the record with the provided ID.
        """
        statement = select(self.model).where(obj_id == self.model.id)  # type: ignore
        target_object = db.scalar(statement)

        if target_object:
            target_object.is_deleted = True
            target_object.is_active = False
            target_object.deleted_at = datetime.utcnow()
            db.add(target_object)
            db.commit()

        return target_object
