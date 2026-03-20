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
from src.core.exercises.seed_data import DEFAULT_EXERCISE_DEFINITIONS
from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup
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


def _sample_command(**kwargs: object) -> CreateExerciseCommand:
    defaults: dict[str, object] = {
        "name": "Push-up",
        "description": "Test",
        "exercise_type": ExerciseType.FORCE,
        "muscle_groups": [MuscleGroup.PECTORAUX, MuscleGroup.TRICEPS],
        "difficulty": Difficulty.DEBUTANT,
        "equipment": "poids_du_corps",
        "estimated_duration": 5,
    }
    defaults.update(kwargs)
    return CreateExerciseCommand(**defaults)


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

    async def list_all(
        self,
        *,
        exercise_type: ExerciseType | None = None,
        muscle_group: MuscleGroup | None = None,
        difficulty: Difficulty | None = None,
    ) -> list[Exercise]:
        items = list(self._items.values())
        if exercise_type is not None:
            items = [e for e in items if e.exercise_type == exercise_type]
        if muscle_group is not None:
            items = [e for e in items if muscle_group in e.muscle_groups]
        if difficulty is not None:
            items = [e for e in items if e.difficulty == difficulty]
        return items

    async def upsert_many(self, exercises: list[Exercise]) -> None:
        for ex in exercises:
            existing = await self.get_by_name(ex.name)
            if existing is not None:
                merged = ex.model_copy(
                    update={
                        "id": existing.id,
                        "created_at": existing.created_at,
                    },
                )
                self._items[existing.id] = merged
            else:
                self._items[ex.id] = ex


@pytest.mark.asyncio()
async def test_create_exercise_enforces_uniqueness() -> None:
    repo = InMemoryExerciseRepository()
    handler = CreateExerciseHandler(FakeDateTime(), repo, FakeUUID())

    command = _sample_command()
    exercise = await handler.handle(command)
    assert exercise.name == "Push-up"
    assert exercise.exercise_type == ExerciseType.FORCE

    with pytest.raises(ConflictError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_update_exercise_changes_fields() -> None:
    repo = InMemoryExerciseRepository()
    create_handler = CreateExerciseHandler(FakeDateTime(), repo, FakeUUID())
    stored = await create_handler.handle(
        _sample_command(name="Squat", description="Bodyweight"),
    )

    update_handler = UpdateExerciseHandler(FakeDateTime(), repo)
    updated = await update_handler.handle(
        UpdateExerciseCommand(
            exercise_id=stored.id,
            name="Air Squat",
            description="Updated",
            exercise_type=ExerciseType.ENDURANCE,
        ),
    )

    assert updated.name == "Air Squat"
    assert updated.description == "Updated"
    assert updated.exercise_type == ExerciseType.ENDURANCE


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
        _sample_command(name="Plank", description="Core"),
    )

    delete_handler = DeleteExerciseHandler(repo)
    await delete_handler.handle(DeleteExerciseCommand(exercise_id=stored.id))

    assert await repo.get_by_id(stored.id) is None


@pytest.mark.asyncio()
async def test_list_all_filters_by_type_and_muscle() -> None:
    repo = InMemoryExerciseRepository()
    h = CreateExerciseHandler(FakeDateTime(), repo, FakeUUID())
    await h.handle(
        _sample_command(
            name="A",
            exercise_type=ExerciseType.CARDIO,
            muscle_groups=[MuscleGroup.JAMBES],
        ),
    )
    await h.handle(
        _sample_command(
            name="B",
            exercise_type=ExerciseType.FORCE,
            muscle_groups=[MuscleGroup.PECTORAUX],
        ),
    )

    cardio = await repo.list_all(exercise_type=ExerciseType.CARDIO)
    assert len(cardio) == 1
    assert cardio[0].name == "A"

    pec = await repo.list_all(muscle_group=MuscleGroup.PECTORAUX)
    assert len(pec) == 1
    assert pec[0].name == "B"


@pytest.mark.asyncio()
async def test_upsert_many_is_idempotent_by_name() -> None:
    repo = InMemoryExerciseRepository()
    dt = FakeDateTime()
    now = dt.utcnow()
    ex_a = Exercise(
        id=UUID(int=1),
        name="Same",
        description="v1",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=[MuscleGroup.ABDOS],
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=5,
        created_at=now,
        updated_at=now,
    )
    ex_b = Exercise(
        id=UUID(int=2),
        name="Same",
        description="v2",
        exercise_type=ExerciseType.CARDIO,
        muscle_groups=[MuscleGroup.JAMBES],
        difficulty=Difficulty.AVANCE,
        equipment="none",
        estimated_duration=20,
        created_at=now,
        updated_at=now,
    )
    await repo.upsert_many([ex_a])
    await repo.upsert_many([ex_b])
    all_rows = list(repo._items.values())
    assert len(all_rows) == 1
    assert all_rows[0].description == "v2"
    assert all_rows[0].exercise_type == ExerciseType.CARDIO
    assert all_rows[0].id == UUID(int=1)


def test_default_seed_has_thirty_exercises() -> None:
    assert len(DEFAULT_EXERCISE_DEFINITIONS) == 30
