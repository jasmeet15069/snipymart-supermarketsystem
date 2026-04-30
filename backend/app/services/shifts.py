from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models.domain import CashierShift, Payment, PaymentMode, ShiftStatus, User
from app.schemas.shift import ShiftCloseRequest, ShiftOpenRequest
from app.services.decimal_utils import money


def get_open_shift(db: Session, cashier_id: int) -> CashierShift | None:
    return db.scalar(
        select(CashierShift).where(CashierShift.cashier_id == cashier_id, CashierShift.status == ShiftStatus.OPEN)
    )


def open_shift(db: Session, current_user: User, payload: ShiftOpenRequest) -> CashierShift:
    if get_open_shift(db, current_user.id):
        raise BusinessError("A shift is already open for this cashier")
    shift = CashierShift(cashier_id=current_user.id, opening_cash=money(payload.opening_cash))
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def close_shift(db: Session, current_user: User, shift_id: int, payload: ShiftCloseRequest) -> CashierShift:
    shift = db.get(CashierShift, shift_id)
    if not shift or shift.cashier_id != current_user.id:
        raise BusinessError("Shift not found", 404)
    if shift.status == ShiftStatus.CLOSED:
        raise BusinessError("Shift is already closed")

    cash_sales = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .join(Payment.sale)
        .where(Payment.mode == PaymentMode.CASH, Payment.sale.has(shift_id=shift.id))
    )
    expected_cash = money(shift.opening_cash + Decimal(str(cash_sales or 0)))
    shift.closing_cash = money(payload.closing_cash)
    shift.expected_cash = expected_cash
    shift.variance = money(shift.closing_cash - expected_cash)
    shift.status = ShiftStatus.CLOSED
    db.commit()
    db.refresh(shift)
    return shift
