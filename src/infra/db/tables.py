from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Table(DeclarativeBase): ...


class UserTable(Table):
    __tablename__ = "user_account"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))
    oauth_provider: Mapped[str | None] = mapped_column(String(32))
    oauth_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExerciseTable(Table):
    __tablename__ = "exercise"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text())
    exercise_type: Mapped[str] = mapped_column(String(32), index=True)
    muscle_groups: Mapped[list[str]] = mapped_column(ARRAY(String(32)))
    difficulty: Mapped[str] = mapped_column(String(32), index=True)
    equipment: Mapped[str] = mapped_column(String(128))
    estimated_duration: Mapped[int] = mapped_column(Integer())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProgramTable(Table):
    __tablename__ = "program"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    description: Mapped[str] = mapped_column(Text())
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"),
        index=True,
    )
    duration_weeks: Mapped[int] = mapped_column(Integer())
    frequency_per_week: Mapped[int] = mapped_column(Integer())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SessionTemplateTable(Table):
    __tablename__ = "session_template"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    program_id: Mapped[UUID] = mapped_column(
        ForeignKey("program.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128))
    order: Mapped[int] = mapped_column(Integer())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExerciseConfigTable(Table):
    __tablename__ = "exercise_config"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    session_template_id: Mapped[UUID] = mapped_column(
        ForeignKey("session_template.id", ondelete="CASCADE"),
        index=True,
    )
    exercise_id: Mapped[UUID] = mapped_column(
        ForeignKey("exercise.id", ondelete="CASCADE"),
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer())
    rest_seconds: Mapped[int] = mapped_column(Integer(), default=60)
    duration_seconds: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SeriesConfigTable(Table):
    __tablename__ = "series_config"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    exercise_config_id: Mapped[UUID] = mapped_column(
        ForeignKey("exercise_config.id", ondelete="CASCADE"),
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer())
    reps: Mapped[int] = mapped_column(Integer())
    weight: Mapped[float | None] = mapped_column(Float(), nullable=True)
