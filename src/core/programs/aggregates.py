from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SeriesConfig(BaseModel):
    """Configuration d'une série : répétitions + poids optionnel."""

    order: int = Field(ge=1)
    reps: int = Field(gt=0)
    weight: float | None = Field(default=None, ge=0)


class ExerciseConfig(BaseModel):
    """Configuration d'un exercice dans une séance (value object)."""

    exercise_id: UUID
    order: int = Field(ge=1)
    series: list[SeriesConfig] = Field(min_length=1)
    rest_seconds: int = Field(default=60, ge=0)
    duration_seconds: int | None = Field(default=None, ge=0)

    @property
    def sets_count(self) -> int:
        return len(self.series)


class SessionTemplate(BaseModel):
    """Modèle d'une séance dans un programme (entité enfant)."""

    id: UUID
    name: str = Field(min_length=1, max_length=128)
    order: int = Field(ge=1)
    exercises: list[ExerciseConfig] = Field(min_length=1)


class Program(BaseModel):
    """Aggregate root : programme d'entraînement."""

    id: UUID
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=2048)
    owner_id: UUID
    duration_weeks: int = Field(gt=0)
    frequency_per_week: int = Field(ge=1, le=7)
    sessions: list[SessionTemplate] = Field(min_length=1)
    created_at: datetime
    updated_at: datetime

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "duration_weeks": self.duration_weeks,
            "frequency_per_week": self.frequency_per_week,
            "sessions": [
                {
                    "id": s.id,
                    "name": s.name,
                    "order": s.order,
                    "exercises": [
                        {
                            "exercise_id": e.exercise_id,
                            "order": e.order,
                            "sets_count": e.sets_count,
                            "series": [
                                {
                                    "order": se.order,
                                    "reps": se.reps,
                                    "weight": se.weight,
                                }
                                for se in e.series
                            ],
                            "rest_seconds": e.rest_seconds,
                            "duration_seconds": e.duration_seconds,
                        }
                        for e in s.exercises
                    ],
                }
                for s in self.sessions
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
