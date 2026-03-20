from typing import NamedTuple
from uuid import UUID

from cq import command_handler
from pydantic import BaseModel, Field, field_validator

from src.core.exercises.aggregates import Exercise
from src.core.exercises.ports.repo import ExerciseRepository
from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup
from src.exceptions import ApplicationError, ConflictError
from src.services.datetime.abc import DateTimeService


class UpdateExerciseCommand(BaseModel):
    exercise_id: UUID
    name: str | None = None
    description: str | None = None
    exercise_type: ExerciseType | None = None
    muscle_groups: list[MuscleGroup] | None = None
    difficulty: Difficulty | None = None
    equipment: str | None = Field(default=None, max_length=128)
    estimated_duration: int | None = Field(default=None, ge=1, le=1440)

    @field_validator("name", "description", "equipment")
    @classmethod
    def _strip(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


@command_handler
class UpdateExerciseHandler(NamedTuple):
    datetime: DateTimeService
    repo: ExerciseRepository

    async def handle(self, command: UpdateExerciseCommand) -> Exercise:
        exercise = await self.repo.get_by_id(command.exercise_id)

        if exercise is None:
            raise ApplicationError("Exercice introuvable.", http_status=404)

        if command.name is not None and command.name != exercise.name:
            taken = await self.repo.get_by_name(command.name)
            if taken is not None and taken.id != exercise.id:
                raise ConflictError("Un exercice avec ce nom existe déjà.")

        data: dict[str, object] = {"updated_at": self.datetime.utcnow()}

        if command.name is not None:
            data["name"] = command.name

        if command.description is not None:
            data["description"] = command.description

        if command.exercise_type is not None:
            data["exercise_type"] = command.exercise_type

        if command.muscle_groups is not None:
            if len(command.muscle_groups) == 0:
                raise ApplicationError(
                    "Au moins un groupe musculaire est requis.",
                    http_status=422,
                )
            data["muscle_groups"] = command.muscle_groups

        if command.difficulty is not None:
            data["difficulty"] = command.difficulty

        if command.equipment is not None:
            data["equipment"] = command.equipment

        if command.estimated_duration is not None:
            data["estimated_duration"] = command.estimated_duration

        updated = exercise.model_copy(update=data)
        await self.repo.update(updated)
        return updated
