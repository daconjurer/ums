import uuid
from typing import Protocol, TypeVar

from ums.db.async_connection import AsyncDatabaseSession
from ums.domain.entities import Base
from ums.middlewares.filter_sort import BaseFilterParams, SortParams

Entity = TypeVar("Entity", bound=Base)


class ReaderInterface(Protocol[Entity]):
    """Interface for read operations."""

    async def get(
        self,
        db: AsyncDatabaseSession,
        id: uuid.UUID,
    ) -> Entity | None:
        ...

    async def get_by(
        self,
        db: AsyncDatabaseSession,
        filter: BaseFilterParams,
    ) -> Entity | None:
        ...

    async def get_many(
        self,
        db: AsyncDatabaseSession,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = 5,
        offset: int | None = 1,
    ) -> list[Entity]:
        ...


class WriterInterface(Protocol[Entity]):
    """Interface for write operations."""

    async def create(
        self,
        db: AsyncDatabaseSession,
        entity: Entity,
    ) -> Entity:
        ...

    # async def update(
    #     self,
    #     db: AsyncDatabaseSession,
    #     data: Entity,
    # ) -> Entity:
    #     ...

    # async def delete(
    #     self,
    #     db: AsyncDatabaseSession,
    #     id: uuid.UUID,
    # ) -> None:
    #     ...
