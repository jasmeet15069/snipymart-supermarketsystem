"""Repair legacy flat sales table.

Revision ID: 0002_repair_legacy_sales_table
Revises: 0001_initial
Create Date: 2026-04-30
"""

from __future__ import annotations

from datetime import datetime, timezone

from alembic import op
from sqlalchemy import inspect, text

from app.models import Base

revision = "0002_repair_legacy_sales_table"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


DEPENDENT_TABLES = [
    "sale_return_items",
    "sale_returns",
    "sale_item_batch_allocations",
    "payments",
    "sale_items",
    "loyalty_ledger",
]

RECREATE_TABLES = [
    "sales",
    "sale_items",
    "sale_item_batch_allocations",
    "payments",
    "sale_returns",
    "sale_return_items",
    "loyalty_ledger",
]


def _table_exists(table_name: str) -> bool:
    return inspect(op.get_bind()).has_table(table_name)


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _count_rows(table_name: str) -> int:
    return int(op.get_bind().execute(text(f"SELECT COUNT(*) FROM `{table_name}`")).scalar() or 0)


def _next_legacy_name() -> str:
    base_name = "legacy_sales_flat"
    if not _table_exists(base_name):
        return base_name
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{base_name}_{suffix}"


def upgrade() -> None:
    if not _table_exists("sales"):
        Base.metadata.create_all(
            bind=op.get_bind(),
            tables=[Base.metadata.tables[name] for name in RECREATE_TABLES],
        )
        return

    sales_columns = _columns("sales")
    current_sales_columns = {"invoice_number", "cashier_id", "grand_total", "paid_total"}
    if current_sales_columns.issubset(sales_columns):
        Base.metadata.create_all(bind=op.get_bind())
        return

    non_empty_dependents = [
        table_name
        for table_name in DEPENDENT_TABLES
        if _table_exists(table_name) and _count_rows(table_name) > 0
    ]
    if non_empty_dependents:
        joined = ", ".join(non_empty_dependents)
        raise RuntimeError(
            "Cannot automatically repair legacy sales schema because dependent "
            f"tables contain data: {joined}. Back up and migrate those rows first."
        )

    for table_name in DEPENDENT_TABLES:
        if _table_exists(table_name):
            op.drop_table(table_name)

    op.rename_table("sales", _next_legacy_name())
    Base.metadata.create_all(
        bind=op.get_bind(),
        tables=[Base.metadata.tables[name] for name in RECREATE_TABLES],
    )


def downgrade() -> None:
    # The upgrade preserves the legacy flat sales rows in a backup table. Reversing
    # that shape safely is data-dependent, so downgrade intentionally leaves data
    # untouched.
    pass
