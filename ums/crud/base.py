"""Base CRUD module.

Provides the base functionality for typical CRUD operations.
"""
import sys
import uuid
from datetime import datetime
from typing import Any, Generic, Type, TypeVar

from loguru import logger
from pydantic import BaseModel

if sys.version_info > (3, 11):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc

from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, SQLModel, select

from ums.core.exceptions import UMSException
from ums.middlewares.filter_sort import BaseFilterParams, SortParams
from ums.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class CreateSchema(SQLModel):
    ...


class UpdateSchema(SQLModel):
    ...


class BaseRepository(BaseModel, Generic[ModelType]):
    """CRUD repository with default methods."""

    model: Type[ModelType]
    filter_params: Type[BaseFilterParams] | None = None
    sort_options: tuple[str, ...] | None = None

    @property
    def filter_params_dict(self) -> dict[str, Any]:
        if not self.filter_params:
            return {}
        return {
            attr: getattr(self.model, attr)
            for attr in self.filter_params.model_fields.keys()
        }

    @property
    def sort_params_dict(self) -> dict[str, Any]:
        if not self.sort_options:
            return {}
        return {attr: getattr(self.model, attr) for attr in self.sort_options}

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
        filter: BaseFilterParams,
    ) -> Base | None:
        """Read operation.

        Fetches a record by a filter key-value pair.
        """
        filters = filter.get_filters()

        if len(filters) > 1:
            raise UMSException(
                status_code=400,
                detail="Only one filter is allowed for this operation.",
            )

        for key, value in filters.items():
            filter_field = self.filter_params_dict.get(key)
            if filter_field:
                statement = select(self.model).where(filter_field == value)
                return db.scalar(statement)
        return None

    def get_many(
        self,
        db: Session,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> list[Base]:
        """Read operation.

        Fetches a list of records from the database with optional filtering,
         sorting and pagination.
        """
        statement = select(self.model)

        if filter and self.filter_params:
            filters = filter.get_filters()
            for key, value in filters.items():
                filter_field = self.filter_params_dict.get(key)
                if filter_field:
                    statement = statement.where(filter_field == value)

        # Apply sorting
        if sort and self.sort_options:
            column_to_sort = self.sort_params_dict.get(sort.sort_by, None)
            if column_to_sort:
                statement = statement.order_by(
                    column_to_sort.asc()
                    if sort.sort_order == "asc"
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

        setattr(db_obj, "updated_at", datetime.now(tz=UTC))

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
            target_object.deleted_at = datetime.now(tz=UTC)
            db.add(target_object)
            db.commit()

        return target_object
