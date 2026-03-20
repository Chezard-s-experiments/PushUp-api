from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup


class Exercise(BaseModel):
    id: UUID
    name: str
    description: str
    exercise_type: ExerciseType
    muscle_groups: list[MuscleGroup]
    difficulty: Difficulty
    equipment: str
    estimated_duration: int = Field(
        ge=1, le=1440, description="Durée estimée en minutes"
    )
    created_at: datetime
    updated_at: datetime

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.exercise_type.value,
            "muscle_groups": [m.value for m in self.muscle_groups],
            "difficulty": self.difficulty.value,
            "equipment": self.equipment,
            "estimated_duration": self.estimated_duration,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
