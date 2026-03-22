from dataclasses import dataclass
from uuid import UUID

from injection import injectable
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.programs.aggregates import (
    ExerciseConfig,
    Program,
    SeriesConfig,
    SessionTemplate,
)
from src.core.programs.ports.repo import ProgramRepository
from src.infra.db.tables import (
    ExerciseConfigTable,
    ProgramTable,
    SeriesConfigTable,
    SessionTemplateTable,
)
from src.services.uuid.abc import UUIDGenerator


@injectable(on=ProgramRepository)
@dataclass(frozen=True)
class SQLAProgramRepository(ProgramRepository):
    session: AsyncSession
    uuid: UUIDGenerator

    async def add(self, program: Program) -> None:
        now = program.created_at
        stmt = insert(ProgramTable).values(
            id=program.id,
            name=program.name,
            description=program.description,
            owner_id=program.owner_id,
            duration_weeks=program.duration_weeks,
            frequency_per_week=program.frequency_per_week,
            created_at=now,
            updated_at=now,
        )
        await self.session.execute(stmt)
        await self._insert_children(program)

    async def update(self, program: Program) -> None:
        await self.session.merge(
            ProgramTable(
                id=program.id,
                name=program.name,
                description=program.description,
                owner_id=program.owner_id,
                duration_weeks=program.duration_weeks,
                frequency_per_week=program.frequency_per_week,
                created_at=program.created_at,
                updated_at=program.updated_at,
            )
        )
        await self._delete_children(program.id)
        await self._insert_children(program)

    async def delete(self, program_id: UUID) -> None:
        stmt = delete(ProgramTable).where(ProgramTable.id == program_id)
        await self.session.execute(stmt)

    async def get_by_id(self, program_id: UUID) -> Program | None:
        stmt = select(ProgramTable).where(ProgramTable.id == program_id)
        program_row = (await self.session.execute(stmt)).scalar_one_or_none()
        if program_row is None:
            return None
        return await self._load_aggregate(program_row)

    async def list_by_owner(self, owner_id: UUID) -> list[Program]:
        stmt = (
            select(ProgramTable)
            .where(ProgramTable.owner_id == owner_id)
            .order_by(ProgramTable.created_at.desc())
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return [await self._load_aggregate(row) for row in rows]

    # -- private helpers --

    async def _insert_children(self, program: Program) -> None:
        now = program.updated_at
        for session in program.sessions:
            session_id = session.id
            await self.session.execute(
                insert(SessionTemplateTable).values(
                    id=session_id,
                    program_id=program.id,
                    name=session.name,
                    order=session.order,
                    created_at=now,
                    updated_at=now,
                )
            )
            for exercise in session.exercises:
                ec_id = self.uuid.next()
                await self.session.execute(
                    insert(ExerciseConfigTable).values(
                        id=ec_id,
                        session_template_id=session_id,
                        exercise_id=exercise.exercise_id,
                        order=exercise.order,
                        rest_seconds=exercise.rest_seconds,
                        duration_seconds=exercise.duration_seconds,
                        created_at=now,
                        updated_at=now,
                    )
                )
                for series in exercise.series:
                    await self.session.execute(
                        insert(SeriesConfigTable).values(
                            id=self.uuid.next(),
                            exercise_config_id=ec_id,
                            order=series.order,
                            reps=series.reps,
                            weight=series.weight,
                        )
                    )

    async def _delete_children(self, program_id: UUID) -> None:
        sessions_stmt = select(SessionTemplateTable.id).where(
            SessionTemplateTable.program_id == program_id,
        )
        session_ids = (await self.session.execute(sessions_stmt)).scalars().all()
        if not session_ids:
            return

        ec_stmt = select(ExerciseConfigTable.id).where(
            ExerciseConfigTable.session_template_id.in_(session_ids),
        )
        ec_ids = (await self.session.execute(ec_stmt)).scalars().all()

        if ec_ids:
            await self.session.execute(
                delete(SeriesConfigTable).where(
                    SeriesConfigTable.exercise_config_id.in_(ec_ids),
                )
            )
            await self.session.execute(
                delete(ExerciseConfigTable).where(
                    ExerciseConfigTable.id.in_(ec_ids),
                )
            )

        await self.session.execute(
            delete(SessionTemplateTable).where(
                SessionTemplateTable.id.in_(session_ids),
            )
        )

    async def _load_aggregate(self, row: ProgramTable) -> Program:
        sessions_stmt = (
            select(SessionTemplateTable)
            .where(SessionTemplateTable.program_id == row.id)
            .order_by(SessionTemplateTable.order)
        )
        session_rows = (await self.session.execute(sessions_stmt)).scalars().all()

        sessions: list[SessionTemplate] = []
        for s_row in session_rows:
            ec_stmt = (
                select(ExerciseConfigTable)
                .where(
                    ExerciseConfigTable.session_template_id == s_row.id,
                )
                .order_by(ExerciseConfigTable.order)
            )
            ec_rows = (await self.session.execute(ec_stmt)).scalars().all()

            exercises: list[ExerciseConfig] = []
            for ec_row in ec_rows:
                sc_stmt = (
                    select(SeriesConfigTable)
                    .where(
                        SeriesConfigTable.exercise_config_id == ec_row.id,
                    )
                    .order_by(SeriesConfigTable.order)
                )
                sc_rows = (await self.session.execute(sc_stmt)).scalars().all()
                series = [
                    SeriesConfig(
                        order=sc.order,
                        reps=sc.reps,
                        weight=sc.weight,
                    )
                    for sc in sc_rows
                ]
                exercises.append(
                    ExerciseConfig(
                        exercise_id=ec_row.exercise_id,
                        order=ec_row.order,
                        series=series,
                        rest_seconds=ec_row.rest_seconds,
                        duration_seconds=ec_row.duration_seconds,
                    )
                )

            sessions.append(
                SessionTemplate(
                    id=s_row.id,
                    name=s_row.name,
                    order=s_row.order,
                    exercises=exercises,
                )
            )

        return Program(
            id=row.id,
            name=row.name,
            description=row.description,
            owner_id=row.owner_id,
            duration_weeks=row.duration_weeks,
            frequency_per_week=row.frequency_per_week,
            sessions=sessions,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
