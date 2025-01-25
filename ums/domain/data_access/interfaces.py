import uuid
from typing import Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from ums.core.filter_sort import BaseFilterParams, SortParams
from ums.domain.entities import Base

Entity = TypeVar("Entity", bound=Base)


class IRead(Protocol[Entity]):
    """Interface for operations that read from the database."""

    async def get(
        self,
        db: AsyncSession,
        id: uuid.UUID,
    ) -> Entity | None:
        ...

    async def get_by(
        self,
        db: AsyncSession,
        filter: BaseFilterParams,
    ) -> Entity | None:
        ...

    async def get_many(
        self,
        db: AsyncSession,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int | None = 5,
        page: int | None = 1,
    ) -> list[Entity]:
        ...


class IWrite(Protocol[Entity]):
    """Interface for operations that change the state of the database."""

    async def create(
        self,
        db: AsyncSession,
        entity: Entity,
    ) -> Entity:
        ...

    # async def update(
    #     self,
    #     db: AsyncSession,
    #     data: Entity,
    # ) -> Entity:
    #     ...

    # async def delete(
    #     self,
    #     db: AsyncSession,
    #     id: uuid.UUID,
    # ) -> None:
    #     ...
