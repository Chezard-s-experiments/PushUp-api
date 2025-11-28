from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from src.core.exercises.aggregates import Exercise


class ExerciseRepository(Protocol):
    @abstractmethod
    async def add(self, exercise: Exercise) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, exercise: Exercise) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, exercise_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, exercise_id: UUID) -> Exercise | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Exercise | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[Exercise]:
        raise NotImplementedError
