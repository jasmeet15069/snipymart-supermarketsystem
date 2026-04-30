from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.domain import ShiftStatus
from app.schemas.common import ORMModel


class ShiftOpenRequest(BaseModel):
    opening_cash: Decimal = Field(default=Decimal("0.00"), ge=0)


class ShiftCloseRequest(BaseModel):
    closing_cash: Decimal = Field(ge=0)


class ShiftRead(ORMModel):
    id: int
    cashier_id: int
    status: ShiftStatus
    opened_at: datetime
    closed_at: datetime | None
    opening_cash: Decimal
    closing_cash: Decimal | None
    expected_cash: Decimal | None
    variance: Decimal | None
