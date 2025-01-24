from enum import Enum
from typing import Literal, Type
from sqlmodel import SQLModel

from pydantic import BaseModel

# Filtering

FilterType = str | int | bool
FilterMap = dict[str, FilterType]
SortMap = dict[str, str]


class BaseFilterParams(BaseModel):
    """
    Base class for filter parameters (this is the parameters container to be
    used in the query).

    When subclassing, define the filter parameters as fields.
    """

class FilterMapper:
    def get_filters(self, params: BaseFilterParams) -> dict[str, FilterType]:
        return params.model_dump(exclude_none=True, exclude_unset=True)

    def get_map(self, params: BaseFilterParams, model: Type[SQLModel]) -> FilterMap:
        return {
            attr: getattr(model, attr)
            for attr in params.model_fields.keys()
        }

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


class SortMapper:
    def __init__(self, options: Type[SortOptions]):
        self.sort_options = list(options.__members__.keys())

    def get_map(self, model: Type[SQLModel]) -> SortMap:
        return {attr: getattr(model, attr) for attr in self.sort_options}
