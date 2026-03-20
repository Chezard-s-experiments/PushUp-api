"""Exercise metadata: type, muscles, difficulty, equipment, duration.

Revision ID: 2b8c9e1a4f00
Revises: 354fd7177754
Create Date: 2026-03-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2b8c9e1a4f00"
down_revision: Union[str, Sequence[str], None] = "354fd7177754"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "exercise",
        sa.Column(
            "exercise_type",
            sa.String(length=32),
            nullable=False,
            server_default="force",
        ),
    )
    op.add_column(
        "exercise",
        sa.Column(
            "muscle_groups",
            postgresql.ARRAY(sa.String(length=32)),
            nullable=False,
            server_default=sa.text("ARRAY[]::varchar[]"),
        ),
    )
    op.add_column(
        "exercise",
        sa.Column(
            "difficulty",
            sa.String(length=32),
            nullable=False,
            server_default="debutant",
        ),
    )
    op.add_column(
        "exercise",
        sa.Column(
            "equipment",
            sa.String(length=128),
            nullable=False,
            server_default="poids_du_corps",
        ),
    )
    op.add_column(
        "exercise",
        sa.Column(
            "estimated_duration",
            sa.Integer(),
            nullable=False,
            server_default="10",
        ),
    )
    op.create_index(
        op.f("ix_exercise_exercise_type"),
        "exercise",
        ["exercise_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_exercise_difficulty"),
        "exercise",
        ["difficulty"],
        unique=False,
    )
    op.alter_column("exercise", "exercise_type", server_default=None)
    op.alter_column("exercise", "muscle_groups", server_default=None)
    op.alter_column("exercise", "difficulty", server_default=None)
    op.alter_column("exercise", "equipment", server_default=None)
    op.alter_column("exercise", "estimated_duration", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_exercise_difficulty"), table_name="exercise")
    op.drop_index(op.f("ix_exercise_exercise_type"), table_name="exercise")
    op.drop_column("exercise", "estimated_duration")
    op.drop_column("exercise", "equipment")
    op.drop_column("exercise", "difficulty")
    op.drop_column("exercise", "muscle_groups")
    op.drop_column("exercise", "exercise_type")
