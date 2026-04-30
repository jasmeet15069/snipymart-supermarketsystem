from decimal import Decimal

from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    today_revenue: Decimal
    month_revenue: Decimal
    today_sales_count: int
    low_stock_count: int
    open_purchase_orders: int
    active_customers: int


class RevenuePoint(BaseModel):
    period: str
    revenue: Decimal
    sales_count: int


class TopProduct(BaseModel):
    product_id: int
    product_name: str
    sku: str
    quantity_sold: Decimal
    revenue: Decimal
