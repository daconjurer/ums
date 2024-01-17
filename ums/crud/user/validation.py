from typing import Any
from sqlmodel import select
from ums.db.session import Session
from ums.core import exceptions
from ums.crud.base import CreateSchema, UpdateSchema
from ums.models import Group, Role


class UserValidator:
    """Validates a UserCreate or UserUpdate object."""

    def validate(
        self, db: Session, input_object: CreateSchema | UpdateSchema
    ) -> dict[str, Any]:
        input_object_data = input_object.model_dump()

        # Check role_id is valid
        if input_object_data.get("role_id"):
            statement = select(Role).where(Role.id == input_object_data["role_id"])
            role = db.scalar(statement)

            if not role:
                raise exceptions.InvalidRoleException("Invalid role_id")

            input_object_data["role_id"] = role.id

        # Check groups_ids are valid
        user_groups = []
        if input_object_data.get("groups_ids"):
            statement = select(Group).where(Group.is_active == True)  # type: ignore
            active_groups = db.scalars(statement).all()

            if active_groups:
                active_group_ids_set = {group.id for group in active_groups}
                input_group_ids_set = set(input_object_data["groups_ids"])

                invalid_group_ids = input_group_ids_set - active_group_ids_set

                if invalid_group_ids:
                    raise exceptions.InvalidGroupException(
                        f"Invalid group_id: {invalid_group_ids.pop()}"
                    )

                user_groups = [
                    group for group in active_groups if group.id in input_group_ids_set
                ]

        # Assign groups
        input_object_data.pop("groups_ids")
        input_object_data["groups"] = user_groups

        return input_object_data
