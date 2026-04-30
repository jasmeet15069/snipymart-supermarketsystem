from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.domain import (
    Customer,
    InventoryItem,
    Product,
    PurchaseOrder,
    PurchaseOrderStatus,
    Sale,
    SaleItem,
    SaleStatus,
)
from app.schemas.reports import DashboardMetrics, RevenuePoint, TopProduct
from app.services.decimal_utils import money


def dashboard_metrics(db: Session) -> DashboardMetrics:
    today_start = datetime.combine(date.today(), time.min)
    month_start = today_start.replace(day=1)
    valid_sales = Sale.status != SaleStatus.VOID
    today_revenue = db.scalar(select(func.coalesce(func.sum(Sale.grand_total), 0)).where(valid_sales, Sale.created_at >= today_start))
    month_revenue = db.scalar(select(func.coalesce(func.sum(Sale.grand_total), 0)).where(valid_sales, Sale.created_at >= month_start))
    today_sales_count = db.scalar(select(func.count(Sale.id)).where(valid_sales, Sale.created_at >= today_start))
    low_stock_count = db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.on_hand < InventoryItem.reorder_level))
    open_purchase_orders = db.scalar(
        select(func.count(PurchaseOrder.id)).where(PurchaseOrder.status.in_([PurchaseOrderStatus.ORDERED, PurchaseOrderStatus.PARTIAL]))
    )
    active_customers = db.scalar(select(func.count(Customer.id)).where(Customer.is_active.is_(True)))
    return DashboardMetrics(
        today_revenue=money(today_revenue or 0),
        month_revenue=money(month_revenue or 0),
        today_sales_count=int(today_sales_count or 0),
        low_stock_count=int(low_stock_count or 0),
        open_purchase_orders=int(open_purchase_orders or 0),
        active_customers=int(active_customers or 0),
    )


def revenue_series(db: Session, days: int = 30) -> list[RevenuePoint]:
    start = datetime.combine(date.today() - timedelta(days=days - 1), time.min)
    rows = db.execute(
        select(func.date(Sale.created_at), func.coalesce(func.sum(Sale.grand_total), 0), func.count(Sale.id))
        .where(Sale.status != SaleStatus.VOID, Sale.created_at >= start)
        .group_by(func.date(Sale.created_at))
        .order_by(func.date(Sale.created_at))
    ).all()
    return [RevenuePoint(period=str(period), revenue=money(revenue), sales_count=int(count)) for period, revenue, count in rows]


def top_products(db: Session, limit: int = 10) -> list[TopProduct]:
    rows = db.execute(
        select(Product.id, Product.name, Product.sku, func.coalesce(func.sum(SaleItem.quantity), 0), func.coalesce(func.sum(SaleItem.line_total), 0))
        .join(SaleItem.product)
        .join(SaleItem.sale)
        .where(Sale.status != SaleStatus.VOID)
        .group_by(Product.id, Product.name, Product.sku)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(limit)
    ).all()
    return [
        TopProduct(product_id=pid, product_name=name, sku=sku, quantity_sold=Decimal(str(qty_sold)), revenue=money(revenue))
        for pid, name, sku, qty_sold, revenue in rows
    ]
