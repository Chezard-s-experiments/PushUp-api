"""Tests d'intégration : soft delete du programme (repository réel)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.programs.aggregates import (
    ExerciseConfig,
    Program,
    SeriesConfig,
    SessionTemplate,
)
from src.infra.adapters.programs.repo import SQLAProgramRepository
from src.infra.db.tables import ExerciseTable, ProgramTable, UserTable
from src.services.uuid.ulid import ULIDGenerator

_NOW = datetime(2025, 6, 1, tzinfo=UTC)


async def _insert_user(session: AsyncSession) -> UUID:
    user_id = uuid4()
    await session.execute(
        insert(UserTable).values(
            id=user_id,
            email=f"user-{user_id}@example.com",
            password_hash="$argon2id$v=19$m=65536,t=3,p=4$fakesalt$fakehash",
            first_name="Test",
            last_name="User",
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return user_id


async def _insert_exercise(session: AsyncSession) -> UUID:
    exercise_id = uuid4()
    await session.execute(
        insert(ExerciseTable).values(
            id=exercise_id,
            name=f"Exercice-{exercise_id}",
            description="Exercice de test",
            exercise_type="force",
            muscle_groups=["pectoraux"],
            difficulty="debutant",
            equipment="poids_du_corps",
            estimated_duration=5,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return exercise_id


def _make_program(*, owner_id: UUID, exercise_id: UUID) -> Program:
    return Program(
        id=uuid4(),
        name="Programme intégration",
        description="Programme pour test d'intégration",
        owner_id=owner_id,
        duration_weeks=4,
        frequency_per_week=3,
        sessions=[
            SessionTemplate(
                id=uuid4(),
                name="Séance A",
                order=1,
                exercises=[
                    ExerciseConfig(
                        exercise_id=exercise_id,
                        order=1,
                        series=[SeriesConfig(order=1, reps=10)],
                    )
                ],
            )
        ],
        created_at=_NOW,
        updated_at=_NOW,
    )


@pytest.mark.asyncio
async def test_soft_delete_hides_program_from_get_by_id(
    db_session: AsyncSession,
) -> None:
    owner_id = await _insert_user(db_session)
    exercise_id = await _insert_exercise(db_session)
    repo = SQLAProgramRepository(session=db_session, uuid=ULIDGenerator())
    program = _make_program(owner_id=owner_id, exercise_id=exercise_id)

    await repo.add(program)
    assert await repo.get_by_id(program.id) is not None

    await repo.soft_delete(program.id)

    assert await repo.get_by_id(program.id) is None


@pytest.mark.asyncio
async def test_soft_delete_preserves_row_in_db(
    db_session: AsyncSession,
) -> None:
    owner_id = await _insert_user(db_session)
    exercise_id = await _insert_exercise(db_session)
    repo = SQLAProgramRepository(session=db_session, uuid=ULIDGenerator())
    program = _make_program(owner_id=owner_id, exercise_id=exercise_id)

    await repo.add(program)
    await repo.soft_delete(program.id)

    row = (
        await db_session.execute(
            select(ProgramTable).where(ProgramTable.id == program.id)
        )
    ).scalar_one_or_none()

    assert row is not None
    assert row.deleted_at is not None


@pytest.mark.asyncio
async def test_hard_delete_removes_row_from_db(
    db_session: AsyncSession,
) -> None:
    owner_id = await _insert_user(db_session)
    exercise_id = await _insert_exercise(db_session)
    repo = SQLAProgramRepository(session=db_session, uuid=ULIDGenerator())
    program = _make_program(owner_id=owner_id, exercise_id=exercise_id)

    await repo.add(program)
    await repo.delete(program.id)

    row = (
        await db_session.execute(
            select(ProgramTable).where(ProgramTable.id == program.id)
        )
    ).scalar_one_or_none()

    assert row is None


@pytest.mark.asyncio
async def test_soft_deleted_program_excluded_from_list_by_owner(
    db_session: AsyncSession,
) -> None:
    owner_id = await _insert_user(db_session)
    exercise_id = await _insert_exercise(db_session)
    repo = SQLAProgramRepository(session=db_session, uuid=ULIDGenerator())

    prog_a = _make_program(owner_id=owner_id, exercise_id=exercise_id)
    prog_b = _make_program(owner_id=owner_id, exercise_id=exercise_id)
    await repo.add(prog_a)
    await repo.add(prog_b)

    await repo.soft_delete(prog_a.id)

    visible = await repo.list_by_owner(owner_id)
    assert len(visible) == 1
    assert visible[0].id == prog_b.id


@pytest.mark.asyncio
async def test_has_completed_sessions_returns_false(
    db_session: AsyncSession,
) -> None:
    owner_id = await _insert_user(db_session)
    exercise_id = await _insert_exercise(db_session)
    repo = SQLAProgramRepository(session=db_session, uuid=ULIDGenerator())
    program = _make_program(owner_id=owner_id, exercise_id=exercise_id)

    await repo.add(program)
    result = await repo.has_completed_sessions(program.id)

    assert result is False
