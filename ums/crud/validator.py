from abc import ABC, abstractmethod
from typing import Any

from ums.crud.base import CreateSchema, UpdateSchema
from ums.db.async_connection import AsyncDatabaseSession


class IValidator(ABC):
    """An object validator interface."""

    @abstractmethod
    def validate(
        self,
        db: AsyncDatabaseSession,
        input_object: CreateSchema | UpdateSchema,
    ) -> dict[str, Any]:
        raise NotImplementedError("Method must be implemented by subclass.")
