from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_admin
from app.schemas.reports import DashboardMetrics, RevenuePoint, TopProduct
from app.services.reports import dashboard_metrics, revenue_series, top_products

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(require_admin)])


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(db: Session = Depends(get_db)) -> DashboardMetrics:
    return dashboard_metrics(db)


@router.get("/revenue", response_model=list[RevenuePoint])
def revenue(days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db)) -> list[RevenuePoint]:
    return revenue_series(db, days)


@router.get("/top-products", response_model=list[TopProduct])
def top_products_route(limit: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)) -> list[TopProduct]:
    return top_products(db, limit)
