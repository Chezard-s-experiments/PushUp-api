from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SeriesConfigRead(BaseModel):
    order: int
    reps: int
    weight: float | None


class ExerciseConfigRead(BaseModel):
    exercise_id: UUID
    order: int
    sets_count: int
    series: list[SeriesConfigRead]
    rest_seconds: int
    duration_seconds: int | None


class SessionTemplateRead(BaseModel):
    id: UUID
    name: str
    order: int
    exercises: list[ExerciseConfigRead]


class ProgramRead(BaseModel):
    id: UUID
    name: str
    description: str
    owner_id: UUID
    duration_weeks: int
    frequency_per_week: int
    sessions: list[SessionTemplateRead]
    created_at: datetime
    updated_at: datetime


class ProgramListView(BaseModel):
    items: list[ProgramRead]
