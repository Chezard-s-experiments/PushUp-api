"""Tests unitaires pour DeleteProgramHandler (soft delete vs hard delete)."""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from src.core.programs.aggregates import (
    ExerciseConfig,
    Program,
    SeriesConfig,
    SessionTemplate,
)
from src.core.programs.commands.delete_program import (
    DeleteProgramCommand,
    DeleteProgramHandler,
)
from src.core.programs.exceptions import ProgramNotFoundError
from src.core.programs.ports.repo import ProgramRepository
from src.exceptions import ForbiddenError

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_OWNER_ID = UUID(int=10)
_OTHER_ID = UUID(int=20)
_PROGRAM_ID = UUID(int=1)


def _make_program(
    *, program_id: UUID = _PROGRAM_ID, owner_id: UUID = _OWNER_ID
) -> Program:
    return Program(
        id=program_id,
        name="Programme test",
        description="Description du programme",
        owner_id=owner_id,
        duration_weeks=8,
        frequency_per_week=3,
        sessions=[
            SessionTemplate(
                id=UUID(int=200),
                name="Séance A",
                order=1,
                exercises=[
                    ExerciseConfig(
                        exercise_id=UUID(int=100),
                        order=1,
                        series=[SeriesConfig(order=1, reps=10)],
                    )
                ],
            )
        ],
        created_at=_NOW,
        updated_at=_NOW,
    )


class FakeProgramRepository(ProgramRepository):
    def __init__(self, *, has_sessions: bool = False) -> None:
        self._items: dict[UUID, Program] = {}
        self._soft_deleted: set[UUID] = set()
        self._has_sessions = has_sessions

    async def add(self, program: Program) -> None:
        self._items[program.id] = program

    async def update(self, program: Program) -> None:
        self._items[program.id] = program

    async def delete(self, program_id: UUID) -> None:
        self._items.pop(program_id, None)
        self._soft_deleted.discard(program_id)

    async def soft_delete(self, program_id: UUID) -> None:
        self._soft_deleted.add(program_id)

    async def has_completed_sessions(self, program_id: UUID) -> bool:
        return self._has_sessions

    async def get_by_id(self, program_id: UUID) -> Program | None:
        if program_id in self._soft_deleted:
            return None
        return self._items.get(program_id)

    async def list_by_owner(self, owner_id: UUID) -> list[Program]:
        return [
            p
            for p in self._items.values()
            if p.owner_id == owner_id and p.id not in self._soft_deleted
        ]


@pytest.mark.asyncio()
async def test_delete_program_not_found_raises() -> None:
    repo = FakeProgramRepository()
    handler = DeleteProgramHandler(repo=repo)

    with pytest.raises(ProgramNotFoundError):
        await handler.handle(
            DeleteProgramCommand(program_id=UUID(int=999), owner_id=_OWNER_ID)
        )


@pytest.mark.asyncio()
async def test_delete_program_wrong_owner_raises_forbidden() -> None:
    repo = FakeProgramRepository()
    await repo.add(_make_program())

    handler = DeleteProgramHandler(repo=repo)

    with pytest.raises(ForbiddenError):
        await handler.handle(
            DeleteProgramCommand(program_id=_PROGRAM_ID, owner_id=_OTHER_ID)
        )


@pytest.mark.asyncio()
async def test_delete_program_without_sessions_performs_hard_delete() -> None:
    repo = FakeProgramRepository(has_sessions=False)
    await repo.add(_make_program())

    handler = DeleteProgramHandler(repo=repo)
    await handler.handle(
        DeleteProgramCommand(program_id=_PROGRAM_ID, owner_id=_OWNER_ID)
    )

    assert await repo.get_by_id(_PROGRAM_ID) is None
    assert _PROGRAM_ID not in repo._items


@pytest.mark.asyncio()
async def test_delete_program_with_sessions_performs_soft_delete() -> None:
    repo = FakeProgramRepository(has_sessions=True)
    await repo.add(_make_program())

    handler = DeleteProgramHandler(repo=repo)
    await handler.handle(
        DeleteProgramCommand(program_id=_PROGRAM_ID, owner_id=_OWNER_ID)
    )

    assert await repo.get_by_id(_PROGRAM_ID) is None
    assert _PROGRAM_ID in repo._items
    assert _PROGRAM_ID in repo._soft_deleted


@pytest.mark.asyncio()
async def test_soft_deleted_program_hidden_from_list() -> None:
    repo = FakeProgramRepository(has_sessions=True)
    await repo.add(_make_program(program_id=UUID(int=1)))
    await repo.add(_make_program(program_id=UUID(int=2)))

    handler = DeleteProgramHandler(repo=repo)
    await handler.handle(
        DeleteProgramCommand(program_id=UUID(int=1), owner_id=_OWNER_ID)
    )

    visible = await repo.list_by_owner(_OWNER_ID)
    assert len(visible) == 1
    assert visible[0].id == UUID(int=2)
