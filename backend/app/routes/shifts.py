from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.domain import User
from app.schemas.shift import ShiftCloseRequest, ShiftOpenRequest, ShiftRead
from app.services.shifts import close_shift, get_open_shift, open_shift

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.get("/current", response_model=ShiftRead | None)
def current_shift(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_open_shift(db, current_user.id)


@router.post("/open", response_model=ShiftRead)
def open_shift_route(payload: ShiftOpenRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return open_shift(db, current_user, payload)


@router.post("/{shift_id}/close", response_model=ShiftRead)
def close_shift_route(
    shift_id: int,
    payload: ShiftCloseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return close_shift(db, current_user, shift_id, payload)
