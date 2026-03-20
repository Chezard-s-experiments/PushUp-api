from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup


class ExerciseRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    description: str
    exercise_type: ExerciseType = Field(alias="type")
    muscle_groups: list[MuscleGroup]
    difficulty: Difficulty
    equipment: str
    estimated_duration: int
    created_at: datetime
    updated_at: datetime


class ExerciseListView(BaseModel):
    items: list[ExerciseRead]
