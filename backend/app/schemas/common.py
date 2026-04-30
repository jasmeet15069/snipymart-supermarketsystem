from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


Quantity = Decimal
Money = Decimal


class Page(ORMModel):
    items: list
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=200)
