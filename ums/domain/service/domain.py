from typing import Generic

from ums.core.data_access.interfaces import Entity
from ums.core.data_access.reader import GenericReader
from ums.core.data_access.writer import GenericWriter
from ums.core.db.async_session import AsyncSessionStream, AsyncSessionStreamProvider, db
from ums.domain.service.interfaces import IService


class DomainService(IService, Generic[Entity]):
    reader: GenericReader[Entity]
    writer: GenericWriter[Entity]

    def __init__(
        self,
        db: AsyncSessionStreamProvider = db,
    ):
        self.db: AsyncSessionStream = db()
