from functools import lru_cache

from pydantic import Field

from ums.settings.api import APISettings
from ums.settings.base import CommonSettings
from ums.settings.postgres import PostgresSettings
from ums.settings.security import SecuritySettings


class AppSettings(CommonSettings):
    api: APISettings = APISettings()
    security: SecuritySettings = SecuritySettings()
    db: PostgresSettings = PostgresSettings()

    environment: str = Field(validation_alias="ENVIRONMENT", default="dev")
    project_name: str = "UMS (User Management System)"
    project_description: str = "A FastAPI-based API for user management."


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
