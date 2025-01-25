import uuid
from typing import Protocol, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ums.core.filter_sort import BaseFilterParams, SortParams
from ums.db.async_session import AsyncSessionStream
from ums.domain.entities import Base

Entity = TypeVar("Entity", bound=Base)


class IRead(Protocol[Entity]):
    """Interface for operations that read from the database."""

    async def get(
        self,
        db: AsyncSessionStream,
        id: uuid.UUID,
    ) -> Entity | None:
        ...

    async def get_by(
        self,
        db: AsyncSessionStream,
        filter: BaseFilterParams,
    ) -> Entity | None:
        ...

    async def get_many(
        self,
        db: AsyncSessionStream,
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
        session: AsyncSession,
        entity: Entity,
    ) -> Entity:
        ...

    # async def update(
    #     self,
    #     session: AsyncSession,
    #     data: Entity,
    # ) -> Entity:
    #     ...

    # async def delete(
    #     self,
    #     session: AsyncSession,
    #     id: uuid.UUID,
    # ) -> None:
    #     ...


class Schema(BaseModel):
    ...
