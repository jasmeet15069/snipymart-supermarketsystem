"""Add business columns for supermarket workflows.

Revision ID: 0003_business_table_enhancements
Revises: 0002_repair_legacy_sales_table
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0003_business_table_enhancements"
down_revision = "0002_repair_legacy_sales_table"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    return inspect(op.get_bind()).has_table(table_name)


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(column["name"] == column_name for column in inspect(op.get_bind()).get_columns(table_name))


def _add_column(table_name: str, column: sa.Column) -> None:
    if not _column_exists(table_name, column.name):
        op.add_column(table_name, column)


def _drop_column(table_name: str, column_name: str) -> None:
    if _column_exists(table_name, column_name):
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    _add_column("categories", sa.Column("description", sa.String(length=255), nullable=True))

    _add_column("products", sa.Column("brand", sa.String(length=80), nullable=True))
    _add_column("products", sa.Column("hsn_code", sa.String(length=20), nullable=True))
    _add_column("products", sa.Column("shelf_location", sa.String(length=60), nullable=True))
    _add_column("products", sa.Column("min_margin_percent", sa.Numeric(5, 2), nullable=False, server_default="12.00"))

    _add_column("inventory_items", sa.Column("safety_stock", sa.Numeric(12, 3), nullable=False, server_default="0.000"))

    _add_column("inventory_batches", sa.Column("supplier_batch_code", sa.String(length=120), nullable=True))
    _add_column("inventory_batches", sa.Column("mrp", sa.Numeric(12, 2), nullable=True))

    _add_column("customers", sa.Column("loyalty_tier", sa.String(length=30), nullable=False, server_default="REGULAR"))
    _add_column("customers", sa.Column("credit_limit", sa.Numeric(12, 2), nullable=False, server_default="0.00"))

    _add_column("suppliers", sa.Column("payment_terms", sa.String(length=80), nullable=True))
    _add_column("suppliers", sa.Column("credit_days", sa.Integer(), nullable=False, server_default="0"))

    _add_column("sales", sa.Column("channel", sa.String(length=30), nullable=False, server_default="POS"))
    _add_column("sales", sa.Column("payment_status", sa.String(length=30), nullable=False, server_default="PAID"))

    _add_column("purchase_orders", sa.Column("payment_status", sa.String(length=30), nullable=False, server_default="UNPAID"))


def downgrade() -> None:
    _drop_column("purchase_orders", "payment_status")
    _drop_column("sales", "payment_status")
    _drop_column("sales", "channel")
    _drop_column("suppliers", "credit_days")
    _drop_column("suppliers", "payment_terms")
    _drop_column("customers", "credit_limit")
    _drop_column("customers", "loyalty_tier")
    _drop_column("inventory_batches", "mrp")
    _drop_column("inventory_batches", "supplier_batch_code")
    _drop_column("inventory_items", "safety_stock")
    _drop_column("products", "min_margin_percent")
    _drop_column("products", "shelf_location")
    _drop_column("products", "hsn_code")
    _drop_column("products", "brand")
    _drop_column("categories", "description")
