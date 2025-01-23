import asyncio
import uuid

from loguru import logger

from ums.core.security import get_password_hash
from ums.db.async_session import get_async_session
from ums.domain.entities import Permissions, User
from ums.domain.permissions.reader import permissions_reader
from ums.domain.permissions.writer import permissions_writer
from ums.domain.user.reader import user_reader
from ums.domain.user.writer import user_writer


async def create_user_and_permissions():
    async with get_async_session() as session:
        _ = await user_writer.create(
            session,
            User(
                id=uuid.UUID("4b65e643-ca72-44b8-a29b-6de42a70079c"),
                name="TestUser",
                full_name="Test User",
                email="test.user@rfs-example.com",
                password=get_password_hash("verysafepassword69"),
                groups=[],
            ),
        )
        _ = await permissions_writer.create(
            session,
            Permissions(
                id=uuid.UUID("201d8cdb-42f2-45ae-8283-bf62725826ac"),
                name="users",
                description="List all the users",
            ),
        )
        await session.commit()


async def get_user_and_permissions():
    async with get_async_session() as session:
        user = await user_reader.get(
            session, uuid.UUID("4b65e643-ca72-44b8-a29b-6de42a70079c")
        )
        logger.info(user)
        permissions = await permissions_reader.get(
            session, uuid.UUID("201d8cdb-42f2-45ae-8283-bf62725826ac")
        )
        logger.info(permissions)
        await session.commit()


async def create_and_get_user_and_permissions():
    await create_user_and_permissions()
    await get_user_and_permissions()


if __name__ == "__main__":
    asyncio.run(create_and_get_user_and_permissions())
