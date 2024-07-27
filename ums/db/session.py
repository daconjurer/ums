from sqlalchemy.orm import close_all_sessions
from sqlmodel import Session, create_engine

from ums.models import Base
from ums.settings.application import get_app_settings

db_settings = get_app_settings().db

engine = create_engine(
    str(db_settings.uri),
    pool_pre_ping=True,
)

Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def setup_db():
    Base.metadata.create_all(engine)


def drop_db():
    close_all_sessions()
    Base.metadata.drop_all(engine)
