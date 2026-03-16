"""empty message

Revision ID: 354fd7177754
Revises: 0001_initial
Create Date: 2025-11-25 17:33:34.641191

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "354fd7177754"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user_account",
        sa.Column("oauth_provider", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "user_account",
        sa.Column("oauth_id", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user_account", "oauth_id")
    op.drop_column("user_account", "oauth_provider")
