from typing import NamedTuple

from cq import query_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exercises.dtos import ExerciseRead
from src.core.exercises.queries.get_exercise import GetExerciseQuery
from src.infra.db.tables import ExerciseTable


@query_handler
class GetExerciseHandler(NamedTuple):
    session: AsyncSession

    async def handle(
        self,
        query: GetExerciseQuery,
    ) -> ExerciseRead | None:
        stmt = select(
            ExerciseTable.id,
            ExerciseTable.name,
            ExerciseTable.description,
            ExerciseTable.created_at,
            ExerciseTable.updated_at,
        ).where(ExerciseTable.id == query.exercise_id)

        row = (await self.session.execute(stmt)).mappings().one_or_none()

        if row is None:
            return None

        return ExerciseRead.model_validate(row)
