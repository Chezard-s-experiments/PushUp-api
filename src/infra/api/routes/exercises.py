from typing import Annotated
from uuid import UUID

from cq import CommandBus, QueryBus
from fastapi import APIRouter, Depends, HTTPException, Query, status
from injection.ext.fastapi import Inject
from pydantic import BaseModel, Field

from src.core.exercises.aggregates import Exercise
from src.core.exercises.commands.create_exercise import CreateExerciseCommand
from src.core.exercises.commands.delete_exercise import DeleteExerciseCommand
from src.core.exercises.commands.update_exercise import UpdateExerciseCommand
from src.core.exercises.dtos import ExerciseListView, ExerciseRead
from src.core.exercises.queries.get_exercise import GetExerciseQuery
from src.core.exercises.queries.list_exercises import ListExercisesQuery
from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup
from src.infra.api.dependencies import require_auth

router = APIRouter(prefix="/exercises", tags=["Exercises"])


class ExercisePayload(BaseModel):
    model_config = {"populate_by_name": True}

    name: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=2048)
    exercise_type: ExerciseType = Field(alias="type")
    muscle_groups: list[MuscleGroup] = Field(min_length=1)
    difficulty: Difficulty
    equipment: str = Field(min_length=1, max_length=128)
    estimated_duration: int = Field(ge=1, le=1440)


class UpdateExercisePayload(BaseModel):
    model_config = {"populate_by_name": True}

    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, min_length=1, max_length=2048)
    exercise_type: ExerciseType | None = Field(default=None, alias="type")
    muscle_groups: list[MuscleGroup] | None = Field(default=None, min_length=1)
    difficulty: Difficulty | None = None
    equipment: str | None = Field(default=None, min_length=1, max_length=128)
    estimated_duration: int | None = Field(default=None, ge=1, le=1440)


@router.get("", response_model=ExerciseListView)
async def list_exercises(
    query_bus: Inject[QueryBus[ExerciseListView]],
    exercise_type: Annotated[
        ExerciseType | None,
        Query(alias="type"),
    ] = None,
    muscle_group: Annotated[MuscleGroup | None, Query()] = None,
    difficulty: Annotated[Difficulty | None, Query()] = None,
) -> ExerciseListView:
    query = ListExercisesQuery(
        exercise_type=exercise_type,
        muscle_group=muscle_group,
        difficulty=difficulty,
    )
    return await query_bus.dispatch(query)


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(
    exercise_id: UUID,
    query_bus: Inject[QueryBus[ExerciseRead | None]],
) -> ExerciseRead:
    query = GetExerciseQuery(exercise_id=exercise_id)
    exercise = await query_bus.dispatch(query)

    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return exercise


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_auth)],
    response_model=ExerciseRead,
)
async def create_exercise(
    payload: ExercisePayload,
    command_bus: Inject[CommandBus[Exercise]],
) -> ExerciseRead:
    command = CreateExerciseCommand(**payload.model_dump())
    exercise = await command_bus.dispatch(command)
    return ExerciseRead.model_validate(exercise.model_dump())


@router.put(
    "/{exercise_id}",
    dependencies=[Depends(require_auth)],
    response_model=ExerciseRead,
)
async def update_exercise(
    exercise_id: UUID,
    payload: UpdateExercisePayload,
    command_bus: Inject[CommandBus[Exercise]],
) -> ExerciseRead:
    data = payload.model_dump(exclude_none=True)
    command = UpdateExerciseCommand(exercise_id=exercise_id, **data)
    exercise = await command_bus.dispatch(command)
    return ExerciseRead.model_validate(exercise.model_dump())


@router.delete(
    "/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_auth)],
)
async def delete_exercise(
    exercise_id: UUID,
    command_bus: Inject[CommandBus[None]],
) -> None:
    command = DeleteExerciseCommand(exercise_id=exercise_id)
    await command_bus.dispatch(command)
