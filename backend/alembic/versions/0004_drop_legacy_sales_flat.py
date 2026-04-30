"""Drop obsolete legacy flat sales backup table.

Revision ID: 0004_drop_legacy_sales_flat
Revises: 0003_business_table_enhancements
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect

revision = "0004_drop_legacy_sales_flat"
down_revision = "0003_business_table_enhancements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if inspect(op.get_bind()).has_table("legacy_sales_flat"):
        op.drop_table("legacy_sales_flat")


def downgrade() -> None:
    # The legacy table was an obsolete backup of the pre-invoice sales shape.
    # It cannot be reconstructed safely from the normalized sales schema.
    pass
