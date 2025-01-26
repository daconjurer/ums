from sqlmodel import select

from ums.core import exceptions
from ums.db.async_session import AsyncSessionStream
from ums.domain.entities import Group, Role, User
from ums.domain.user.schemas import UserCreate, UserUpdate


class UserValidator:
    """Validates a UserCreate or UserUpdate object."""

    async def validate(
        self,
        db: AsyncSessionStream,
        input: UserCreate | UserUpdate,
    ) -> User:
        # Check role_id is valid
        if input.role_id:
            statement = select(Role).where(Role.id == input.role_id)

            async with db() as session:
                role = await session.scalar(statement)
                await session.commit()

            if not role:
                raise exceptions.InvalidRoleException("Invalid role_id")

            input.role_id = role.id

        # Check groups_ids are valid
        user_groups = []
        if input.groups_ids:
            statement = select(Group).where(Group.is_active == True)  # type: ignore  # noqa: E712

            async with db() as session:
                result = await session.scalars(statement)
                await session.commit()
                active_groups = result.all()

            if active_groups:
                active_group_ids_set = {group.id for group in active_groups}
                input_group_ids_set = set(input.groups_ids)

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
