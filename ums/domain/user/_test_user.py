import asyncio
import uuid

from loguru import logger

from ums.core.security import get_password_hash
from ums.db.async_session import get_async_session
from ums.domain.entities import User
from ums.domain.user.reader import user_reader
from ums.domain.user.writer import user_writer


async def create_user():
    async with get_async_session() as session:
        result = await user_writer.create(
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
        logger.info(result)
        await session.commit()


async def get_user():
    async with get_async_session() as session:
        user = await user_reader.get(
            session, uuid.UUID("4b65e643-ca72-44b8-a29b-6de42a70079c")
        )
        logger.info(user)
        await session.commit()


async def create_and_get_user():
    await create_user()
    await get_user()


if __name__ == "__main__":
    asyncio.run(create_and_get_user())
