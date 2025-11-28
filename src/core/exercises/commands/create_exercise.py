from typing import NamedTuple

from cq import command_handler
from pydantic import BaseModel

from src.core.exercises.aggregates import Exercise
from src.core.exercises.ports.repo import ExerciseRepository
from src.exceptions import ConflictError
from src.services.datetime.abc import DateTimeService
from src.services.uuid.abc import UUIDGenerator


class CreateExerciseCommand(BaseModel):
    name: str
    description: str


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
            name=command.name.strip(),
            description=command.description.strip(),
            created_at=now,
            updated_at=now,
        )
        await self.repo.add(exercise)
        return exercise
