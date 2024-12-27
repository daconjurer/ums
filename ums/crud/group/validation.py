from sqlmodel import select

from ums.core import exceptions
from ums.crud.base import CreateSchema, UpdateSchema
from ums.db.async_connection import AsyncDatabaseSession
from ums.models import User


class GroupValidator:
    """Validates a GroupCreate or GroupUpdate object."""

    async def validate(
        self, db: AsyncDatabaseSession, input_object: CreateSchema | UpdateSchema
    ) -> None:
        input_object_data = input_object.model_dump()

        # Relational integrity validation
        if input_object_data.get("members_ids"):
            input_members_ids = set(input_object_data["members_ids"])
            statement = select(User.id).where(
                User.is_active == True,  # noqa: E712
                User.id.in_(input_members_ids),  # type: ignore[attr-defined]
            )

            async with db() as session:
                result = await session.scalars(statement)
                valid_user_ids = set(result.all())

            if not valid_user_ids:
                invalid_members_ids = input_members_ids - valid_user_ids
                raise exceptions.InvalidUserException(
                    f"Invalid member_ids: {invalid_members_ids.pop()}"
                )
