import asyncio
import uuid
from typing import Sequence

from ums.db.async_session import AsyncSessionStream, db
from ums.domain.entities import User
from ums.domain.group.schemas import GroupUpdate
from ums.domain.group.validator import GroupValidator


async def get_members_by_ids(
    db: AsyncSessionStream,
    member_ids: list[uuid.UUID],
) -> Sequence[User]:
    """Get all active members that match the given IDs."""

    # statement = (
    #     select(User)
    #     .where(
    #         User.id.in_(member_ids),
    #         User.is_active == True,   # noqa: E712
    #         User.is_deleted == False  # noqa: E712
    #     )
    # )

    input = GroupUpdate(
        id=uuid.UUID("d2ae3068-f5c3-4ab8-a1fd-912828963749"),
        member_ids=member_ids,
    )

    validator = GroupValidator()
    members = await validator.validate(db, input)

    # async with db() as session:
    #     result = await session.scalars(statement)
    #     members = list(result.all())

    return members


async def main():
    members = await get_members_by_ids(
        db=db(),
        member_ids=[
            uuid.UUID("f18941a4-bb0e-444a-b6a0-a19509cc6089"),
            uuid.UUID("c3b162a7-e0c1-43d1-a237-037de1c771fd"),
            # uuid.UUID("2fe19756-b3dd-4ca4-9ea9-69852b15c255"),
            uuid.UUID("d2ae3068-f5c3-4ab8-a1fd-912828963749"),
        ],
    )
    print(members)


if __name__ == "__main__":
    asyncio.run(main())
