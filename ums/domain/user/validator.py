from sqlmodel import column, select

from ums.core.db.async_session import AsyncSessionStream
from ums.domain import exceptions
from ums.domain.entities import Group, Role, User
from ums.domain.user.schemas import UserCreate, UserUpdate


class UserValidator:
    """Validates a UserCreate or UserUpdate object."""

    async def validate(
        self,
        db: AsyncSessionStream,
        input: UserCreate | UserUpdate,
    ) -> User:
        # Check role ID is valid
        if input.role_id:
            role_statement = select(Role).where(Role.id == input.role_id)

            async with db() as session:
                role = await session.scalar(role_statement)
                await session.commit()

            if not role:
                raise exceptions.InvalidRoleException("Invalid role_id")

            input.role_id = role.id

        # Check group IDs are valid
        user_groups = []
        if input.group_ids:
            groups_statement = select(Group).where(column("is_active").is_(True))

            async with db() as session:
                result = await session.scalars(groups_statement)
                await session.commit()
                active_groups = result.all()

            if not active_groups:
                raise exceptions.InvalidGroupException("No active groups found")

            active_group_ids_set = {group.id for group in active_groups}
            input_group_ids_set = set(input.group_ids)

            invalid_group_ids = input_group_ids_set - active_group_ids_set

            if invalid_group_ids:
                raise exceptions.InvalidGroupException(
                    f"Invalid group_id: {invalid_group_ids.pop()}"
                )

            user_groups = [
                group for group in active_groups if group.id in input_group_ids_set
            ]

        # Assign groups
        valid_user = User(
            **input.model_dump(exclude_none=True, exclude_unset=True),
            groups=user_groups,
        )

        return valid_user
