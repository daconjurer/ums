from typing import Generic

from ums.data_access.interfaces import Entity
from ums.data_access.reader import GenericReader
from ums.data_access.writer import GenericWriter
from ums.db.async_session import AsyncSessionStream, AsyncSessionStreamProvider, db
from ums.domain.service.interfaces import IService


class DomainService(IService, Generic[Entity]):
    reader: GenericReader[Entity]
    writer: GenericWriter[Entity]

    def __init__(
        self,
        db: AsyncSessionStreamProvider = db,
    ):
        self.db: AsyncSessionStream = db()
