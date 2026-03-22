"""Add program, session_template, exercise_config, series_config tables.

Revision ID: 0004_add_program_tables
Revises: 2b8c9e1a4f00
Create Date: 2026-03-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_add_program_tables"
down_revision: Union[str, Sequence[str], None] = "2b8c9e1a4f00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "program",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("duration_weeks", sa.Integer(), nullable=False),
        sa.Column("frequency_per_week", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user_account.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_program_name"),
        "program",
        ["name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_program_owner_id"),
        "program",
        ["owner_id"],
        unique=False,
    )

    op.create_table(
        "session_template",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("program_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["program_id"],
            ["program.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_session_template_program_id"),
        "session_template",
        ["program_id"],
        unique=False,
    )

    op.create_table(
        "exercise_config",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_template_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("rest_seconds", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_template_id"],
            ["session_template.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercise.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_exercise_config_session_template_id"),
        "exercise_config",
        ["session_template_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_exercise_config_exercise_id"),
        "exercise_config",
        ["exercise_id"],
        unique=False,
    )

    op.create_table(
        "series_config",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("exercise_config_id", sa.Uuid(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["exercise_config_id"],
            ["exercise_config.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_series_config_exercise_config_id"),
        "series_config",
        ["exercise_config_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_series_config_exercise_config_id"),
        table_name="series_config",
    )
    op.drop_table("series_config")
    op.drop_index(
        op.f("ix_exercise_config_exercise_id"),
        table_name="exercise_config",
    )
    op.drop_index(
        op.f("ix_exercise_config_session_template_id"),
        table_name="exercise_config",
    )
    op.drop_table("exercise_config")
    op.drop_index(
        op.f("ix_session_template_program_id"),
        table_name="session_template",
    )
    op.drop_table("session_template")
    op.drop_index(op.f("ix_program_owner_id"), table_name="program")
    op.drop_index(op.f("ix_program_name"), table_name="program")
    op.drop_table("program")
