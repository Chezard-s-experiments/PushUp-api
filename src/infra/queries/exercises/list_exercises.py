from typing import NamedTuple

from cq import query_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exercises.dtos import ExerciseListView, ExerciseRead
from src.core.exercises.queries.list_exercises import ListExercisesQuery
from src.infra.db.tables import ExerciseTable


@query_handler
class ListExercisesHandler(NamedTuple):
    session: AsyncSession

    async def handle(self, query: ListExercisesQuery) -> ExerciseListView:
        stmt = select(
            ExerciseTable.id,
            ExerciseTable.name,
            ExerciseTable.description,
            ExerciseTable.created_at,
            ExerciseTable.updated_at,
        ).order_by(ExerciseTable.created_at.desc())

        rows = (await self.session.execute(stmt)).mappings().all()
        items = [ExerciseRead.model_validate(row) for row in rows]
        return ExerciseListView(items=items)
