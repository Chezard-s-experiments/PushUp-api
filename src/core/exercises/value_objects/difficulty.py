"""Niveau de difficulté d'un exercice."""

from enum import Enum


class Difficulty(str, Enum):
    """Progression : débutant → avancé."""

    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"

    def __str__(self) -> str:
        return self.value
