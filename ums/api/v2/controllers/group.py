from pydantic import BaseModel


class GroupPublic(BaseModel):
    name: str
    description: str | None
