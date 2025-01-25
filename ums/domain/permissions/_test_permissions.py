import asyncio
import uuid

from loguru import logger

from ums.db.async_session import get_async_session
from ums.domain.entities import Permissions
from ums.domain.permissions.reader import permissions_reader
from ums.domain.permissions.writer import permissions_writer


async def create_permissions():
    async with get_async_session() as session:
        result = await permissions_writer.upsert(
            session,
            Permissions(
                id=uuid.UUID("201d8cdb-42f2-45ae-8283-bf62725826ac"),
                name="users",
                description="List all the users",
            ),
        )
        logger.info(result)
        await session.commit()


async def get_permissions():
    async with get_async_session() as session:
        permissions = await permissions_reader.get(
            session, uuid.UUID("201d8cdb-42f2-45ae-8283-bf62725826ac")
        )
        logger.info(permissions)
        await session.commit()


async def create_and_get_permissions():
    await create_permissions()
    await get_permissions()


if __name__ == "__main__":
    asyncio.run(create_and_get_permissions())
