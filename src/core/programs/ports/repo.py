from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from src.core.programs.aggregates import Program


class ProgramRepository(Protocol):
    @abstractmethod
    async def add(self, program: Program) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, program: Program) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, program_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, program_id: UUID) -> Program | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner(self, owner_id: UUID) -> list[Program]:
        raise NotImplementedError
