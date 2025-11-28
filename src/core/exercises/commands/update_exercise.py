from typing import NamedTuple
from uuid import UUID

from cq import command_handler
from pydantic import BaseModel, field_validator

from src.core.exercises.aggregates import Exercise
from src.core.exercises.ports.repo import ExerciseRepository
from src.exceptions import ApplicationError
from src.services.datetime.abc import DateTimeService


class UpdateExerciseCommand(BaseModel):
    exercise_id: UUID
    name: str | None = None
    description: str | None = None

    @field_validator("name", "description")
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

        data: dict[str, object] = {"updated_at": self.datetime.utcnow()}

        if command.name is not None:
            data["name"] = command.name

        if command.description is not None:
            data["description"] = command.description

        updated = exercise.model_copy(update=data)
        await self.repo.update(updated)
        return updated
