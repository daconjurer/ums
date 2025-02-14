import sys
from datetime import datetime
from typing import Type

from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from ums.core.data_access.interfaces import Entity, IWrite

if sys.version_info > (3, 11):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc


class GenericWriter(IWrite[Entity]):
    model: Type[Entity]

    async def create(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        logger.info(f"Creating {self.model.__name__}")

        session.add(entity)
        return entity

    async def update(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        logger.info(f"Updating {self.model.__name__}")
        await session.execute(
            update(self.model)
            .where(self.model.id == entity.id)
            .values(**entity.model_dump())
        )
        return entity

    async def delete(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        logger.info(f"Deleting {self.model.__name__}")

        # Soft delete
        entity.is_deleted = True
        entity.is_active = False
        entity.deleted_at = datetime.now(tz=UTC)

        session.add(entity)

        return entity
