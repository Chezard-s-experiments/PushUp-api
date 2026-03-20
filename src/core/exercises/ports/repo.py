from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from src.core.exercises.aggregates import Exercise
from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup


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
    async def list_all(
        self,
        *,
        exercise_type: ExerciseType | None = None,
        muscle_group: MuscleGroup | None = None,
        difficulty: Difficulty | None = None,
    ) -> list[Exercise]:
        raise NotImplementedError

    @abstractmethod
    async def upsert_many(self, exercises: list[Exercise]) -> None:
        """Insère ou met à jour par nom unique (idempotent)."""
        raise NotImplementedError
