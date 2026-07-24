from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


T = TypeVar("T")


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
    )


class ApiError(ApiModel):
    code: str
    message: str


class PagedResponse(ApiModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
