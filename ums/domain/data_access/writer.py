from typing import Type

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ums.domain.data_access.interfaces import Entity, WriteInterface


class GenericWriter(WriteInterface[Entity]):
    model: Type[Entity]
    # validator: GenericValidator[Entity]

    async def create(
        self,
        db: AsyncSession,
        entity: Entity,
    ) -> Entity:
        logger.info(f"Creating {self.model.__name__}")

        db.add(entity)
