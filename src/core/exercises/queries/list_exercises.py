from pydantic import BaseModel

from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup


class ListExercisesQuery(BaseModel):
    exercise_type: ExerciseType | None = None
    muscle_group: MuscleGroup | None = None
    difficulty: Difficulty | None = None
