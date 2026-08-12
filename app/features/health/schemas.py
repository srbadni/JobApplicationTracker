from typing import Literal

from pydantic import BaseModel


class HealthResult(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
