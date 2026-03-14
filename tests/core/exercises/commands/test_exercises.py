from datetime import UTC, datetime, timezone
from uuid import UUID

import pytest

from src.core.exercises.aggregates import Exercise
from src.core.exercises.commands.create_exercise import (
    CreateExerciseCommand,
    CreateExerciseHandler,
)
from src.core.exercises.commands.delete_exercise import (
    DeleteExerciseCommand,
    DeleteExerciseHandler,
)
from src.core.exercises.commands.update_exercise import (
    UpdateExerciseCommand,
    UpdateExerciseHandler,
)
from src.core.exercises.ports.repo import ExerciseRepository
from src.exceptions import ApplicationError, ConflictError
from src.services.datetime.abc import DateTimeService
from src.services.uuid.abc import UUIDGenerator


class FakeDateTime(DateTimeService):
    def now(self, tz: timezone = UTC) -> datetime:
        return datetime(2025, 1, 1, tzinfo=tz)


class FakeUUID(UUIDGenerator):
    def __init__(self) -> None:
        self.counter = 0

    def next(self) -> UUID:
        self.counter += 1
        return UUID(int=self.counter)


class InMemoryExerciseRepository(ExerciseRepository):
    def __init__(self) -> None:
        self._items: dict[UUID, Exercise] = {}

    async def add(self, exercise: Exercise) -> None:
        self._items[exercise.id] = exercise

    async def update(self, exercise: Exercise) -> None:
        self._items[exercise.id] = exercise

    async def delete(self, exercise_id: UUID) -> None:
        self._items.pop(exercise_id, None)

    async def get_by_id(self, exercise_id: UUID) -> Exercise | None:
        return self._items.get(exercise_id)

    async def get_by_name(self, name: str) -> Exercise | None:
        for item in self._items.values():
            if item.name == name:
                return item
        return None

    async def list_all(self) -> list[Exercise]:
        return list(self._items.values())


@pytest.mark.asyncio()
async def test_create_exercise_enforces_uniqueness() -> None:
    repo = InMemoryExerciseRepository()
    handler = CreateExerciseHandler(FakeDateTime(), repo, FakeUUID())

    command = CreateExerciseCommand(name="Push-up", description="Test")
    exercise = await handler.handle(command)
    assert exercise.name == "Push-up"

    with pytest.raises(ConflictError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_update_exercise_changes_fields() -> None:
    repo = InMemoryExerciseRepository()
    create_handler = CreateExerciseHandler(FakeDateTime(), repo, FakeUUID())
    stored = await create_handler.handle(
        CreateExerciseCommand(name="Squat", description="Bodyweight"),
    )

    update_handler = UpdateExerciseHandler(FakeDateTime(), repo)
    updated = await update_handler.handle(
        UpdateExerciseCommand(
            exercise_id=stored.id,
            name="Air Squat",
            description="Updated",
        )
    )

    assert updated.name == "Air Squat"
    assert updated.description == "Updated"


@pytest.mark.asyncio()
async def test_update_missing_exercise_raises() -> None:
    repo = InMemoryExerciseRepository()
    handler = UpdateExerciseHandler(FakeDateTime(), repo)
    with pytest.raises(ApplicationError):
        await handler.handle(
            UpdateExerciseCommand(exercise_id=UUID(int=42), name="X"),
        )


@pytest.mark.asyncio()
async def test_delete_exercise_removes_entry() -> None:
    repo = InMemoryExerciseRepository()
    create_handler = CreateExerciseHandler(FakeDateTime(), repo, FakeUUID())
    stored = await create_handler.handle(
        CreateExerciseCommand(name="Plank", description="Core"),
    )

    delete_handler = DeleteExerciseHandler(repo)
    await delete_handler.handle(DeleteExerciseCommand(exercise_id=stored.id))

    assert await repo.get_by_id(stored.id) is None
