from sqlmodel import column, select

from ums.core.db.async_session import AsyncSessionStream
from ums.domain import exceptions
from ums.domain.entities import Group, User
from ums.domain.group.schemas import GroupCreate, GroupUpdate


class GroupValidator:
    """Validates a GroupCreate or GroupUpdate object."""

    async def validate(
        self,
        db: AsyncSessionStream,
        input: GroupCreate | GroupUpdate,
    ) -> Group:
        # Check member IDs are valid
        group_members = []

        if input.member_ids:
            statement = select(User).where(
                column("id").in_(input.member_ids),
                column("is_active").is_(True),
                column("is_deleted").is_(False),
            )

            async with db() as session:
                result = await session.scalars(statement)
                await session.commit()
                group_members = list(result.all())

        # No matching members
        if not group_members:
            raise exceptions.InvalidUserException(
                f"Invalid member_id: {input.member_ids.pop()}"
            )

        # Check for invalid member IDs
        group_member_ids_set = {group.id for group in group_members}
        input_member_ids_set = set(input.member_ids)

        invalid_member_ids = input_member_ids_set - group_member_ids_set

        if invalid_member_ids:
            raise exceptions.InvalidUserException(
                f"Invalid member_id: {invalid_member_ids.pop()}"
            )

        # Valid members
        group_members = [
            member for member in group_members if member.id in input_member_ids_set
        ]

        # Assign members
        valid_group = Group(
            **input.model_dump(exclude_none=True, exclude_unset=True),
            members=group_members,
        )

        return valid_group
