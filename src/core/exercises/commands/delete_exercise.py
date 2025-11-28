from typing import NamedTuple
from uuid import UUID

from cq import command_handler
from pydantic import BaseModel

from src.core.exercises.ports.repo import ExerciseRepository


class DeleteExerciseCommand(BaseModel):
    exercise_id: UUID


@command_handler
class DeleteExerciseHandler(NamedTuple):
    repo: ExerciseRepository

    async def handle(self, command: DeleteExerciseCommand) -> None:
        await self.repo.delete(command.exercise_id)
