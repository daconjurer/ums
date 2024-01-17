from pydantic import Field, field_validator, PostgresDsn, ValidationInfo

from ums.settings.base import CommonSettings


class PostgresSettings(CommonSettings):
    user: str | None = Field(validation_alias="POSTGRES_USER", default="")
    password: str | None = Field(validation_alias="POSTGRES_PASSWORD", default="")
    db: str | None = Field(validation_alias="POSTGRES_DB", default="")
    host: str | None = Field(validation_alias="POSTGRES_HOST", default="")
    uri: PostgresDsn | str | None = Field(validation_alias="POSTGRES_URI", default=None)

    @field_validator("uri")
    def assemble_db_uri(cls, v, values: ValidationInfo):
        # .docker.env file
        if isinstance(v, str):
            return v

        # .env file
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("user", ""),
            password=values.data.get("password", ""),
            host=values.data.get("host", ""),
            port=values.data.get("port", 5432),
            path=f'{values.data.get("db", "")}',
        )
