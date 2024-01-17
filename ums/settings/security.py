from pydantic import Field

from ums.settings.base import CommonSettings


class SecuritySettings(CommonSettings):
    secret_key: str = Field(validation_alias="SECRET_KEY", default="")
    hashing_algorithm: str = Field(
        validation_alias="HASHING_ALGORITHM", default="HS256"
    )
    access_token_expire_minutes: int = Field(
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=10
    )
