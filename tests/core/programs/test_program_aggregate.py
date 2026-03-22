from datetime import UTC, datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.core.programs.aggregates import (
    ExerciseConfig,
    Program,
    SeriesConfig,
    SessionTemplate,
)
from src.core.programs.ports.repo import ProgramRepository


class FakeDateTime:
    def now(self, tz: timezone = UTC) -> datetime:
        return datetime(2025, 1, 1, tzinfo=tz)


class FakeUUID:
    def __init__(self) -> None:
        self.counter = 0

    def next(self) -> UUID:
        self.counter += 1
        return UUID(int=self.counter)


def _series(*, order: int = 1, reps: int = 10, weight: float | None = None) -> SeriesConfig:
    return SeriesConfig(order=order, reps=reps, weight=weight)


def _exercise_config(
    *,
    exercise_id: UUID | None = None,
    order: int = 1,
    series: list[SeriesConfig] | None = None,
    rest_seconds: int = 60,
) -> ExerciseConfig:
    return ExerciseConfig(
        exercise_id=exercise_id if exercise_id is not None else UUID(int=100),
        order=order,
        series=series if series is not None else [_series()],
        rest_seconds=rest_seconds,
    )


def _session(
    *,
    session_id: UUID | None = None,
    name: str = "Séance A",
    order: int = 1,
    exercises: list[ExerciseConfig] | None = None,
) -> SessionTemplate:
    return SessionTemplate(
        id=session_id if session_id is not None else UUID(int=200),
        name=name,
        order=order,
        exercises=exercises if exercises is not None else [_exercise_config()],
    )


def _program(
    *,
    program_id: UUID | None = None,
    name: str = "Programme force",
    description: str = "Programme de musculation",
    owner_id: UUID | None = None,
    duration_weeks: int = 8,
    frequency_per_week: int = 3,
    sessions: list[SessionTemplate] | None = None,
) -> Program:
    now = FakeDateTime().now()
    return Program(
        id=program_id if program_id is not None else UUID(int=1),
        name=name,
        description=description,
        owner_id=owner_id if owner_id is not None else UUID(int=10),
        duration_weeks=duration_weeks,
        frequency_per_week=frequency_per_week,
        sessions=sessions if sessions is not None else [_session()],
        created_at=now,
        updated_at=now,
    )


# ── Validation : Program ──


def test_program_requires_at_least_one_session() -> None:
    with pytest.raises(ValidationError, match="sessions"):
        _program(sessions=[])


def test_program_name_cannot_be_empty() -> None:
    with pytest.raises(ValidationError, match="name"):
        _program(name="")


def test_program_name_max_length() -> None:
    with pytest.raises(ValidationError, match="name"):
        _program(name="x" * 129)


def test_program_description_cannot_be_empty() -> None:
    with pytest.raises(ValidationError, match="description"):
        _program(description="")


def test_program_duration_weeks_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="duration_weeks"):
        _program(duration_weeks=0)


def test_program_frequency_per_week_range() -> None:
    with pytest.raises(ValidationError, match="frequency_per_week"):
        _program(frequency_per_week=0)

    with pytest.raises(ValidationError, match="frequency_per_week"):
        _program(frequency_per_week=8)


# ── Validation : SessionTemplate ──


def test_session_requires_at_least_one_exercise() -> None:
    with pytest.raises(ValidationError, match="exercises"):
        _session(exercises=[])


def test_session_name_cannot_be_empty() -> None:
    with pytest.raises(ValidationError, match="name"):
        _session(name="")


def test_session_order_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="order"):
        _session(order=0)


# ── Validation : ExerciseConfig ──


def test_exercise_config_requires_at_least_one_series() -> None:
    with pytest.raises(ValidationError, match="series"):
        _exercise_config(series=[])


def test_exercise_config_order_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="order"):
        _exercise_config(order=0)


def test_exercise_config_rest_seconds_non_negative() -> None:
    with pytest.raises(ValidationError, match="rest_seconds"):
        _exercise_config(rest_seconds=-1)


def test_exercise_config_sets_count_derived() -> None:
    ec = _exercise_config(
        series=[_series(order=1, reps=10), _series(order=2, reps=8)],
    )
    assert ec.sets_count == 2


# ── Validation : SeriesConfig ──


def test_series_reps_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="reps"):
        _series(reps=0)


def test_series_weight_non_negative() -> None:
    with pytest.raises(ValidationError, match="weight"):
        _series(weight=-1.0)


def test_series_weight_optional() -> None:
    s = _series(reps=10)
    assert s.weight is None


def test_series_with_weight() -> None:
    s = _series(reps=10, weight=60.0)
    assert s.weight == 60.0


# ── Nominal : agrégat complet ──


def test_program_nominal_creation() -> None:
    program = _program(
        sessions=[
            _session(
                session_id=UUID(int=200),
                name="Push",
                order=1,
                exercises=[
                    _exercise_config(
                        exercise_id=UUID(int=100),
                        order=1,
                        series=[
                            _series(order=1, reps=10, weight=60.0),
                            _series(order=2, reps=8, weight=70.0),
                            _series(order=3, reps=6, weight=80.0),
                        ],
                        rest_seconds=90,
                    ),
                ],
            ),
            _session(
                session_id=UUID(int=201),
                name="Pull",
                order=2,
                exercises=[
                    _exercise_config(
                        exercise_id=UUID(int=101),
                        order=1,
                        series=[_series(order=1, reps=12)],
                    ),
                ],
            ),
        ],
    )
    assert program.name == "Programme force"
    assert len(program.sessions) == 2
    assert program.sessions[0].exercises[0].sets_count == 3
    assert program.sessions[1].exercises[0].sets_count == 1


def test_program_to_public_dict() -> None:
    program = _program()
    d = program.to_public_dict()

    assert d["id"] == program.id
    assert d["name"] == "Programme force"
    assert d["owner_id"] == program.owner_id

    sessions = d["sessions"]
    assert isinstance(sessions, list)
    assert len(sessions) == 1

    session = sessions[0]
    assert isinstance(session, dict)
    assert session["name"] == "Séance A"

    exercises = session["exercises"]
    assert isinstance(exercises, list)
    assert len(exercises) == 1

    exercise = exercises[0]
    assert isinstance(exercise, dict)
    assert exercise["sets_count"] == 1
    assert isinstance(exercise["series"], list)
    assert len(exercise["series"]) == 1


# ── InMemoryProgramRepository ──


class InMemoryProgramRepository(ProgramRepository):
    def __init__(self) -> None:
        self._items: dict[UUID, Program] = {}

    async def add(self, program: Program) -> None:
        self._items[program.id] = program

    async def update(self, program: Program) -> None:
        self._items[program.id] = program

    async def delete(self, program_id: UUID) -> None:
        self._items.pop(program_id, None)

    async def get_by_id(self, program_id: UUID) -> Program | None:
        return self._items.get(program_id)

    async def list_by_owner(self, owner_id: UUID) -> list[Program]:
        return [p for p in self._items.values() if p.owner_id == owner_id]


@pytest.mark.asyncio()
async def test_repo_add_and_get_by_id() -> None:
    repo = InMemoryProgramRepository()
    program = _program()

    await repo.add(program)
    found = await repo.get_by_id(program.id)

    assert found is not None
    assert found.id == program.id
    assert found.name == program.name
    assert len(found.sessions) == 1


@pytest.mark.asyncio()
async def test_repo_get_by_id_returns_none() -> None:
    repo = InMemoryProgramRepository()
    assert await repo.get_by_id(UUID(int=999)) is None


@pytest.mark.asyncio()
async def test_repo_list_by_owner() -> None:
    repo = InMemoryProgramRepository()
    owner = UUID(int=10)
    other = UUID(int=20)

    await repo.add(_program(program_id=UUID(int=1), owner_id=owner))
    await repo.add(_program(program_id=UUID(int=2), owner_id=owner))
    await repo.add(_program(program_id=UUID(int=3), owner_id=other))

    owned = await repo.list_by_owner(owner)
    assert len(owned) == 2
    assert all(p.owner_id == owner for p in owned)


@pytest.mark.asyncio()
async def test_repo_update() -> None:
    repo = InMemoryProgramRepository()
    program = _program()
    await repo.add(program)

    updated = program.model_copy(
        update={"name": "Nouveau nom", "duration_weeks": 12},
    )
    await repo.update(updated)

    found = await repo.get_by_id(program.id)
    assert found is not None
    assert found.name == "Nouveau nom"
    assert found.duration_weeks == 12


@pytest.mark.asyncio()
async def test_repo_delete() -> None:
    repo = InMemoryProgramRepository()
    program = _program()
    await repo.add(program)

    await repo.delete(program.id)
    assert await repo.get_by_id(program.id) is None
