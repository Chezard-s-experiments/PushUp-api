"""Type d'exercice : force, cardio, endurance, souplesse."""

from enum import Enum


class ExerciseType(str, Enum):
    """Catégorie principale d'un exercice."""

    FORCE = "force"
    CARDIO = "cardio"
    ENDURANCE = "endurance"
    SOUPLESSE = "souplesse"

    def __str__(self) -> str:
        return self.value
