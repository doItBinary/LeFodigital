from typing import Literal

from app.core.schemas import ApiModel


class LiveHealth(ApiModel):
    status: Literal["ok"]


class ReadyHealth(ApiModel):
    status: Literal["ready"]
