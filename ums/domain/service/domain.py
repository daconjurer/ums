from typing import Generic

from ums.db.async_session import AsyncSessionStream, AsyncSessionStreamProvider, db
from ums.domain.data_access.interfaces import Entity
from ums.domain.service.interfaces import IService


class DomainService(IService, Generic[Entity]):
    def __init__(
        self,
        db: AsyncSessionStreamProvider = db,
    ):
        self.db: AsyncSessionStream = db()
