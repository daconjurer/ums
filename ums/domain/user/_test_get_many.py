import asyncio

from loguru import logger

from ums.core.filter_sort import SortParams
from ums.db.async_session import get_async_session
from ums.domain.user.reader import UserFilterParams, user_reader


async def get_user_by_name():
    async with get_async_session() as session:
        result = await user_reader.get_many(
            session,
            UserFilterParams(
                is_active=True,
                is_verified=False,
            ),
            SortParams(
                sort_by="full_name",
                sort_order="asc",
            ),
        )
        await session.commit()
        logger.info(result)


if __name__ == "__main__":
    asyncio.run(get_user_by_name())
