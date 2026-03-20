from dataclasses import dataclass
from uuid import UUID

from injection import injectable
from sqlalchemy import delete, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exercises.aggregates import Exercise
from src.core.exercises.ports.repo import ExerciseRepository
from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup
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

    async def list_all(
        self,
        *,
        exercise_type: ExerciseType | None = None,
        muscle_group: MuscleGroup | None = None,
        difficulty: Difficulty | None = None,
    ) -> list[Exercise]:
        stmt = select(ExerciseTable).order_by(ExerciseTable.created_at)
        if exercise_type is not None:
            stmt = stmt.where(ExerciseTable.exercise_type == exercise_type.value)
        if muscle_group is not None:
            stmt = stmt.where(
                ExerciseTable.muscle_groups.contains([muscle_group.value]),
            )
        if difficulty is not None:
            stmt = stmt.where(ExerciseTable.difficulty == difficulty.value)
        rows = (await self.session.execute(stmt)).scalars().all()
        return [self._from_table(row) for row in rows]

    async def upsert_many(self, exercises: list[Exercise]) -> None:
        for exercise in exercises:
            values = self._to_table_dict(exercise)
            stmt = pg_insert(ExerciseTable).values(**values)
            stmt = stmt.on_conflict_do_update(
                index_elements=["name"],
                set_={
                    "description": stmt.excluded.description,
                    "exercise_type": stmt.excluded.exercise_type,
                    "muscle_groups": stmt.excluded.muscle_groups,
                    "difficulty": stmt.excluded.difficulty,
                    "equipment": stmt.excluded.equipment,
                    "estimated_duration": stmt.excluded.estimated_duration,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            await self.session.execute(stmt)

    def _from_table(self, table: ExerciseTable) -> Exercise:
        return Exercise(
            id=table.id,
            name=table.name,
            description=table.description,
            exercise_type=ExerciseType(table.exercise_type),
            muscle_groups=[MuscleGroup(m) for m in table.muscle_groups],
            difficulty=Difficulty(table.difficulty),
            equipment=table.equipment,
            estimated_duration=table.estimated_duration,
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
            "exercise_type": exercise.exercise_type.value,
            "muscle_groups": [m.value for m in exercise.muscle_groups],
            "difficulty": exercise.difficulty.value,
            "equipment": exercise.equipment,
            "estimated_duration": exercise.estimated_duration,
            "created_at": exercise.created_at,
            "updated_at": exercise.updated_at,
        }
