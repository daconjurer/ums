from enum import Enum

from fastapi import Query
from pydantic import BaseModel

from ums.core.exceptions import InvalidFilteringException


class SortOptions(str, Enum):
    """Available sorting options."""

    asc = "asc"
    desc = "desc"


class SortBy(BaseModel):
    key: str
    by: SortOptions | None = None

    @staticmethod
    def create(keys: list[str]) -> str:
        # allow sorting by a given key: option or no sorting
        allowed_options = "|".join(opt.value for opt in SortOptions)
        allowed_patterns = "|".join(f"{key}:({allowed_options})" for key in keys)
        return f"^({allowed_patterns})$"

    @staticmethod
    def parse(value: str) -> "SortBy":
        by = None
        vals = value.split(":", 1)
        if SortOptions.asc == vals[1]:
            by = SortOptions.asc
        elif SortOptions.desc == vals[1]:
            by = SortOptions.desc

        return SortBy(key=vals[0], by=by)


class FilterBy(BaseModel):
    key: str
    value: str | bool

    @staticmethod
    def parse(value: str) -> "FilterBy":
        vals = value.split(":", 1)
        return FilterBy(key=vals[0], value=vals[1] or "")


def parse_sort(options: list[str]):
    async def _parse_sort(
        sort: str | None = Query(default=None, pattern=SortBy.create(options)),
    ):
        if sort:
            return SortBy.parse(sort)

    return _parse_sort


def parse_filter(options: list[str]):
    async def _parse_filter(filter: list[str] = Query(default=None)):
        if not isinstance(filter, list):
            return []

        for f in filter:
            if not any(f.startswith(opt + ":") for opt in options):
                raise InvalidFilteringException(detail=f"Invalid filter format: {f}")

        resp = [FilterBy.parse(f) for f in filter]

        return resp

    return _parse_filter
