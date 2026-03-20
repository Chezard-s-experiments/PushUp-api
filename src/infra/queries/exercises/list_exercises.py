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
        stmt = (
            select(
                ExerciseTable.id,
                ExerciseTable.name,
                ExerciseTable.description,
                ExerciseTable.exercise_type,
                ExerciseTable.muscle_groups,
                ExerciseTable.difficulty,
                ExerciseTable.equipment,
                ExerciseTable.estimated_duration,
                ExerciseTable.created_at,
                ExerciseTable.updated_at,
            )
            .order_by(ExerciseTable.created_at.desc())
        )
        if query.exercise_type is not None:
            stmt = stmt.where(
                ExerciseTable.exercise_type == query.exercise_type.value,
            )
        if query.muscle_group is not None:
            stmt = stmt.where(
                ExerciseTable.muscle_groups.contains([query.muscle_group.value]),
            )
        if query.difficulty is not None:
            stmt = stmt.where(
                ExerciseTable.difficulty == query.difficulty.value,
            )

        rows = (await self.session.execute(stmt)).mappings().all()
        items = [ExerciseRead.model_validate(dict(row)) for row in rows]
        return ExerciseListView(items=items)
