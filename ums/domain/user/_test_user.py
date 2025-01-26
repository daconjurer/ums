import asyncio
import uuid

from loguru import logger

from ums.core.security import get_password_hash
from ums.db.async_session import AsyncSessionStream, AsyncSessionStreamProvider, db
from ums.domain.entities import User
from ums.domain.user.reader import user_reader
from ums.domain.user.writer import user_writer


async def create_user(db: AsyncSessionStream):
    async with db() as session:
        result = await user_writer.upsert(
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
        await session.commit()
        logger.info(result)


async def get_user(db: AsyncSessionStream):
    user = await user_reader.get(
        db,
        uuid.UUID("4b65e643-ca72-44b8-a29b-6de42a70079c"),
    )
    logger.info(user)


async def update_user(db: AsyncSessionStream):
    user = await user_reader.get(
        db,
        uuid.UUID("4b65e643-ca72-44b8-a29b-6de42a70079c"),
    )

    if not user:
        raise ValueError("User not found")

    user.name = "UpdatedUser"

    async with db() as session:
        await user_writer.upsert(
            session,
            user,
        )
        await session.commit()
        logger.info(user)


async def delete_user(db: AsyncSessionStream):
    user = await user_reader.get(
        db,
        uuid.UUID("4b65e643-ca72-44b8-a29b-6de42a70079c"),
    )

    if not user:
        raise ValueError("User not found")

    async with db() as session:
        await user_writer.delete(
            session,
            user,
        )
        await session.commit()
        logger.info(user)


async def create_and_get_user(db: AsyncSessionStreamProvider):
    await create_user(db=db())
    await get_user(db=db())
    await update_user(db=db())
    await delete_user(db=db())


if __name__ == "__main__":
    asyncio.run(create_and_get_user(db=db))
