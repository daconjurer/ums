from typing import Any

from sqlmodel import select

from ums.core import exceptions
from ums.crud.base import CreateSchema, UpdateSchema
from ums.db.session import Session
from ums.models import User


class GroupValidator:
    """Validates a GroupCreate or GroupUpdate object."""

    def validate(
        self, db: Session, input_object: CreateSchema | UpdateSchema
    ) -> dict[str, Any]:
        input_object_data = input_object.model_dump()

        # Check members_ids are valid
        group_users = []
        if input_object_data.get("members_ids"):
            statement = select(User).where(User.is_active == True)  # noqa: E712
            active_users = db.scalars(statement).all()

            if active_users:
                active_users_ids_set = {user.id for user in active_users}
                input_members_ids_set = set(input_object_data["members_ids"])

                invalid_members_ids = input_members_ids_set - active_users_ids_set

                if invalid_members_ids:
                    raise exceptions.InvalidUserException(
                        f"Invalid member_id: {invalid_members_ids.pop()}"
                    )

                group_users = [
                    group for group in active_users if group.id in input_members_ids_set
                ]

        # Assign users
        input_object_data.pop("members_ids")
        input_object_data["members"] = group_users

        return input_object_data
