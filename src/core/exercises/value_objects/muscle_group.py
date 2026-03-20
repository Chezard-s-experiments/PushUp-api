"""Groupes musculaires ciblés par un exercice."""

from enum import Enum


class MuscleGroup(str, Enum):
    """Zone musculaire (un exercice peut en combiner plusieurs)."""

    PECTORAUX = "pectoraux"
    DOS = "dos"
    EPAULES = "epaules"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    ABDOS = "abdos"
    JAMBES = "jambes"
    FESSIERS = "fessiers"
    MOLLETS = "mollets"
    AVANT_BRAS = "avant_bras"
    CORPS_ENTIER = "corps_entier"

    def __str__(self) -> str:
        return self.value
