import asyncio
import uuid

from loguru import logger

from ums.core.security import get_password_hash
from ums.db.async_session import get_async_session
from ums.domain.user.schemas import UserCreate
from ums.domain.user.validator import UserValidator


async def create_user_with_validator():
    async with get_async_session() as session:
        user_create = UserCreate(
            name="TestUser",
            full_name="Test User",
            email="test.user@rfs-example.com",
            password=get_password_hash("verysafepassword69"),
            role_id=uuid.UUID("f5909109-730c-4701-bd72-f3f6459d9086"),
            groups_ids=[
                uuid.UUID("d2ae3068-f5c3-4ab8-a1fd-912828963749"),
                uuid.UUID("190212f3-35fe-48d2-a3bc-320eee2f0d52"),
            ],
        )

        valid_user = await UserValidator().validate(session, user_create)
        await session.commit()
        logger.info(valid_user)


if __name__ == "__main__":
    asyncio.run(create_user_with_validator())
