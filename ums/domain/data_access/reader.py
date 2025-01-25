import uuid
from typing import Type

from loguru import logger
from sqlalchemy import column, select

from ums.core.exceptions import UMSException
from ums.core.filter_sort import BaseFilterParams, SortParams
from ums.db.async_session import AsyncSessionStream
from ums.domain.data_access.interfaces import Entity, IRead


class GenericReader(IRead[Entity]):
    model: Type[Entity]

    async def get(
        self,
        db: AsyncSessionStream,
        id: uuid.UUID,
    ) -> Entity | None:
        logger.info(f"Getting {self.model.__name__} by ID: {id}")

        statement = select(self.model).where(column("id") == id)

        async with db() as session:
            result = await session.scalar(statement)

        return result

    async def get_by(
        self,
        db: AsyncSessionStream,
        filter: BaseFilterParams,
    ) -> Entity | None:
        """Read operation.

        Fetches a record by a filter key-value pair.
        """

        logger.info(f"Getting one {self.model.__name__} by filter {filter}")

        filters = filter.get_filters()

        if len(filters) > 1:
            raise UMSException(
                status_code=400,
                detail="Only one filter is allowed for this operation.",
            )

        for key, value in filters.items():
            statement = select(self.model).where(column(key) == value)

        async with db() as session:
            result = await session.scalar(statement)

        return result

    async def get_many(
        self,
        db: AsyncSessionStream,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = 5,
        page: int | None = 1,
    ) -> list[Entity]:
        """Read operation.

        Fetches a list of records from the database with optional filtering,
         sorting and pagination.
        """

        logger.info(f"Getting several {self.model.__name__}")

        statement = select(self.model)

        if filter:
            filters = filter.get_filters()

            for key, value in filters.items():
                statement = statement.where(column(key) == value)

        # Apply sorting
        if sort:
            statement = statement.order_by(
                column(sort.sort_by).asc()
                if sort.sort_order == "asc"
                else column(sort.sort_by).desc()
            )

        # Apply pagination
        if page is not None and limit is not None:
            page = 1 if page < 1 else page
            offset = (page - 1) * limit
            statement = statement.offset(offset).limit(limit)

        # Query
        logger.debug(statement.compile(compile_kwargs={"literal_binds": True}))

        async with db() as session:
            entities = await session.scalars(statement)
            result = list(entities.all())

        return result
