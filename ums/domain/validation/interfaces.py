from typing import Protocol, TypeVar

from pydantic import BaseModel

from ums.db.async_connection import AsyncDatabaseSession
from ums.domain.data_access.interfaces import Entity


class Schema(BaseModel):
    ...


TSchema = TypeVar("TSchema", bound=Schema)


class IValidate(Protocol[TSchema, Entity]):
    """An object validator interface."""

    def validate(
        self,
        db: AsyncDatabaseSession,
        input: Schema,
    ) -> Entity:
        ...
