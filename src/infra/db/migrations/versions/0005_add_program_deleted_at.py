"""Add deleted_at column to program table (soft delete support).

Revision ID: 0005_add_program_deleted_at
Revises: 0004_add_program_tables
Create Date: 2026-07-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_add_program_deleted_at"
down_revision: Union[str, Sequence[str], None] = "0004_add_program_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "program",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("program", "deleted_at")
