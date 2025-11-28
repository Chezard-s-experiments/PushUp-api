from dataclasses import dataclass
from uuid import UUID

from injection import injectable
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exercises.aggregates import Exercise
from src.core.exercises.ports.repo import ExerciseRepository
from src.infra.db.tables import ExerciseTable


@injectable(on=ExerciseRepository)
@dataclass(frozen=True)
class SQLAExerciseRepository(ExerciseRepository):
    session: AsyncSession

    async def add(self, exercise: Exercise) -> None:
        stmt = insert(ExerciseTable).values(self._to_table_dict(exercise))
        await self.session.execute(stmt)

    async def update(self, exercise: Exercise) -> None:
        await self.session.merge(self._to_table(exercise))

    async def delete(self, exercise_id: UUID) -> None:
        stmt = delete(ExerciseTable).where(ExerciseTable.id == exercise_id)
        await self.session.execute(stmt)

    async def get_by_id(self, exercise_id: UUID) -> Exercise | None:
        stmt = select(ExerciseTable).where(ExerciseTable.id == exercise_id)
        row = (await self.session.execute(stmt)).scalar_one_or_none()

        if row is None:
            return None

        return self._from_table(row)

    async def get_by_name(self, name: str) -> Exercise | None:
        stmt = select(ExerciseTable).where(ExerciseTable.name == name)
        row = (await self.session.execute(stmt)).scalar_one_or_none()

        if row is None:
            return None

        return self._from_table(row)

    async def list_all(self) -> list[Exercise]:
        stmt = select(ExerciseTable).order_by(ExerciseTable.created_at)
        rows = (await self.session.execute(stmt)).scalars().all()
        return [self._from_table(row) for row in rows]

    def _from_table(self, table: ExerciseTable) -> Exercise:
        return Exercise(
            id=table.id,
            name=table.name,
            description=table.description,
            created_at=table.created_at,
            updated_at=table.updated_at,
        )

    def _to_table(self, exercise: Exercise) -> ExerciseTable:
        return ExerciseTable(**self._to_table_dict(exercise))

    def _to_table_dict(self, exercise: Exercise) -> dict[str, object]:
        return {
            "id": exercise.id,
            "name": exercise.name,
            "description": exercise.description,
            "created_at": exercise.created_at,
            "updated_at": exercise.updated_at,
        }
