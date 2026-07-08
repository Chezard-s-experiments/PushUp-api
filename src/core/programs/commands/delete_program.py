from typing import NamedTuple
from uuid import UUID

from cq import command_handler
from pydantic import BaseModel

from src.core.programs.exceptions import ProgramNotFoundError
from src.core.programs.ports.repo import ProgramRepository
from src.exceptions import ForbiddenError


class DeleteProgramCommand(BaseModel):
    program_id: UUID
    owner_id: UUID


@command_handler
class DeleteProgramHandler(NamedTuple):
    repo: ProgramRepository

    async def handle(self, command: DeleteProgramCommand) -> None:
        program = await self.repo.get_by_id(command.program_id)
        if program is None:
            raise ProgramNotFoundError()

        if program.owner_id != command.owner_id:
            raise ForbiddenError("Vous n'êtes pas autorisé à supprimer ce programme.")

        if await self.repo.has_completed_sessions(command.program_id):
            await self.repo.soft_delete(command.program_id)
        else:
            await self.repo.delete(command.program_id)
