from enum import Enum
from typing import Any, Callable, Literal, Type, TypeAlias, get_args

from fastapi import Query
from pydantic import BaseModel

# Filtering


class BaseFilterParams(BaseModel):
    """
    Base class for filter parameters (this is the parameters container to be
    used in the query).

    When subclassing, define the filter parameters as fields.
    """

    def get_filters(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, exclude_unset=True)


# Sorting

SortOrder = Literal["asc", "desc"]


class SortParams(BaseModel):
    """
    Container class for the sorting parameters. To be populated with the
    `sort_by` and `sort_order` queries.
    """

    sort_by: str
    sort_order: SortOrder


class SortOptions(str, Enum):
    """When subclassing, define the available sorting options."""

    ...


def parse_sorting(options: Type[SortOptions]) -> Callable:
    OptionsAlias: TypeAlias = options  # type: ignore[valid-type]

    async def _parse_sort(
        sort_by: OptionsAlias | None = Query(
            default=None,
            examples=None,
            description=f"A key to sort by. Options: {', '.join(options)}",
        ),
        sort_order: SortOrder | None = Query(
            default=None,
            description=f"Options: {', '.join(list(get_args(SortOrder)))}",
        ),
    ):
        if sort_by:
            return SortParams(
                sort_by=sort_by,
                sort_order=sort_order,
            )

    return _parse_sort
