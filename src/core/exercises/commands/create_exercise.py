from typing import NamedTuple

from cq import command_handler
from pydantic import BaseModel, Field, field_validator

from src.core.exercises.aggregates import Exercise
from src.core.exercises.ports.repo import ExerciseRepository
from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup
from src.exceptions import ConflictError
from src.services.datetime.abc import DateTimeService
from src.services.uuid.abc import UUIDGenerator


class CreateExerciseCommand(BaseModel):
    name: str
    description: str
    exercise_type: ExerciseType
    muscle_groups: list[MuscleGroup] = Field(min_length=1)
    difficulty: Difficulty
    equipment: str = Field(min_length=1, max_length=128)
    estimated_duration: int = Field(ge=1, le=1440)

    @field_validator("name", "description", "equipment")
    @classmethod
    def _strip(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            msg = "La valeur ne peut pas être vide."
            raise ValueError(msg)
        return cleaned


@command_handler
class CreateExerciseHandler(NamedTuple):
    datetime: DateTimeService
    repo: ExerciseRepository
    uuid: UUIDGenerator

    async def handle(self, command: CreateExerciseCommand) -> Exercise:
        existing = await self.repo.get_by_name(command.name)

        if existing:
            raise ConflictError("Un exercice avec ce nom existe déjà.")

        now = self.datetime.utcnow()
        exercise = Exercise(
            id=self.uuid.next(),
            name=command.name,
            description=command.description,
            exercise_type=command.exercise_type,
            muscle_groups=command.muscle_groups,
            difficulty=command.difficulty,
            equipment=command.equipment,
            estimated_duration=command.estimated_duration,
            created_at=now,
            updated_at=now,
        )
        await self.repo.add(exercise)
        return exercise
