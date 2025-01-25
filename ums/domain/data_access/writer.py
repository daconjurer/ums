from typing import Type

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ums.domain.data_access.interfaces import Entity, IWrite


class GenericWriter(IWrite[Entity]):
    model: Type[Entity]

    async def create(
        self,
        session: AsyncSession,
        entity: Entity,
    ) -> Entity:
        logger.info(f"Creating {self.model.__name__}")

        session.add(entity)
        return entity
