import uuid
from typing import Type

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ums.domain.data_access.interfaces import Entity, ReaderInterface
from ums.middlewares.filter_sort import BaseFilterParams, SortParams


class GenericReader(ReaderInterface[Entity]):
    model: Type[Entity]

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
        logger.info(f"Getting one {self.model.__name__} by filter {filter}")

    async def get_many(
        self,
        db: AsyncSession,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = 5,
        offset: int | None = 1,
    ) -> list[Entity]:
        logger.info(f"Getting several {self.model.__name__}")


# async def get(self, db: AsyncDatabaseSession, id: uuid.UUID) -> Base | None:
#     """Read operation.

#     Fetches a single record with the provided ID.

#     Note: This method is very generic and does not consider relationships.
#     If using lazy loading, the session must remain open until the object is used.
#     """
#     statement = select(self.model).where(id == self.model.id)  # type: ignore

#     async with db() as session:
#         result = await session.scalar(statement)

#     return result

# async def get_by(
#     self,
#     db: AsyncDatabaseSession,
#     filter: BaseFilterParams,
# ) -> Base | None:
#     """Read operation.

#     Fetches a record by a filter key-value pair.
#     """
#     filters = filter.get_filters()

#     if len(filters) > 1:
#         raise UMSException(
#             status_code=400,
#             detail="Only one filter is allowed for this operation.",
#         )

#     for key, value in filters.items():
#         filter_field = self.filter_params_dict.get(key)

#         if filter_field:
#             statement = select(self.model).where(filter_field == value)

#             async with db() as session:
#                 return await session.scalar(statement)

#     return None

# async def get_many(
#     self,
#     db: AsyncDatabaseSession,
#     filter: BaseFilterParams | None = None,
#     sort: SortParams | None = None,
#     limit: int | None = 5,
#     page: int | None = 1,
# ) -> list[Base]:
#     """Read operation.

#     Fetches a list of records from the database with optional filtering,
#         sorting and pagination.
#     """
#     statement = select(self.model)

#     if filter and self.filter_params:
#         filters = filter.get_filters()
#         for key, value in filters.items():
#             filter_field = self.filter_params_dict.get(key)
#             if filter_field:
#                 statement = statement.where(filter_field == value)

#     # Apply sorting
#     if sort and self.sort_options:
#         column_to_sort = self.sort_params_dict.get(sort.sort_by, None)
#         if column_to_sort:
#             statement = statement.order_by(
#                 column_to_sort.asc()
#                 if sort.sort_order == "asc"
#                 else column_to_sort.desc()
#             )

#     # Apply pagination
#     if page is not None and limit is not None:
#         page = 1 if page < 1 else page
#         offset = (page - 1) * limit
#         statement = statement.offset(offset).limit(limit)

#     # Query
#     logger.debug(statement.compile(compile_kwargs={"literal_binds": True}))

#     async with db() as session:
#         result = await session.scalars(statement)
#         result = list(result.all())

#     return result
