import uuid
from typing import Type

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ums.core.exceptions import UMSException
from ums.core.filter_sort import BaseFilterParams, FilterMapper, SortMapper, SortParams
from ums.domain.data_access.interfaces import Entity, ReadInterface


class GenericReader(ReadInterface[Entity]):
    model: Type[Entity]
    filter_mapper: FilterMapper | None = None
    sort_mapper: SortMapper | None = None

    async def get(
        self,
        db: AsyncSession,
        id: uuid.UUID,
    ) -> Entity | None:
        logger.info(f"Getting {self.model.__name__} by ID: {id}")

        statement = select(self.model).where(self.model.id == id)
        result = await db.scalar(statement)
        return result

    async def get_by(
        self,
        db: AsyncSession,
        filter: BaseFilterParams,
    ) -> Entity | None:
        """Read operation.

        Fetches a record by a filter key-value pair.
        """

        logger.info(f"Getting one {self.model.__name__} by filter {filter}")

        filters = self.filter_mapper.get_filters(filter)

        if len(filters) > 1:
            raise UMSException(
                status_code=400,
                detail="Only one filter is allowed for this operation.",
            )

        for key, value in filters.items():
            filter_field = self.filter_mapper.get_map(filter, self.model).get(key)

            if filter_field:
                statement = select(self.model).where(filter_field == value)

                return await db.scalar(statement)

        return None

    async def get_many(
        self,
        db: AsyncSession,
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

        if filter and self.filter_mapper:
            filters = self.filter_mapper.get_filters(filter)

            for key, value in filters.items():
                filter_field = self.filter_mapper.get_map(filter, self.model).get(key)
                if filter_field:
                    statement = statement.where(filter_field == value)

        # Apply sorting
        if sort and self.sort_mapper:
            column_to_sort = self.sort_mapper.get_map(self.model).get(
                sort.sort_by, None
            )
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

        result = await db.scalars(statement)
        result = list(result.all())

        return result
