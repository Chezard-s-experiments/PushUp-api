"""Définitions des 30 exercices par défaut (données métier, sans id ni dates)."""

from dataclasses import dataclass

from src.core.exercises.aggregates import Exercise
from src.core.exercises.value_objects import Difficulty, ExerciseType, MuscleGroup
from src.services.datetime.abc import DateTimeService
from src.services.uuid.abc import UUIDGenerator


@dataclass(frozen=True)
class ExerciseSeedDefinition:
    name: str
    description: str
    exercise_type: ExerciseType
    muscle_groups: tuple[MuscleGroup, ...]
    difficulty: Difficulty
    equipment: str
    estimated_duration: int


DEFAULT_EXERCISE_DEFINITIONS: tuple[ExerciseSeedDefinition, ...] = (
    ExerciseSeedDefinition(
        name="Pompes classiques",
        description="Flexions des bras en planche, corps aligné, poitrine près du sol.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.PECTORAUX, MuscleGroup.TRICEPS, MuscleGroup.ABDOS),
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Squat",
        description="Flexion des genoux dos droit, cuisses parallèles au sol.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.FESSIERS),
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Fentes avant",
        description="Pas en avant, genou arrière près du sol, buste gainé.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.FESSIERS),
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=8,
    ),
    ExerciseSeedDefinition(
        name="Planche abdominale",
        description="Maintien sur avant-bras et orteils, corps rigide.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.ABDOS, MuscleGroup.EPAULES),
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=2,
    ),
    ExerciseSeedDefinition(
        name="Burpee",
        description="Squat, planche, pompe optionnelle, saut vertical.",
        exercise_type=ExerciseType.CARDIO,
        muscle_groups=(MuscleGroup.CORPS_ENTIER,),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="poids_du_corps",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Course continue modérée",
        description="Effort aérobie régulier, allure conversationnelle.",
        exercise_type=ExerciseType.ENDURANCE,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.MOLLETS),
        difficulty=Difficulty.DEBUTANT,
        equipment="none",
        estimated_duration=30,
    ),
    ExerciseSeedDefinition(
        name="Corde à sauter",
        description="Sauts légers, poignets moteurs, réceptions souples.",
        exercise_type=ExerciseType.CARDIO,
        muscle_groups=(MuscleGroup.MOLLETS, MuscleGroup.EPAULES),
        difficulty=Difficulty.DEBUTANT,
        equipment="corde",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Développé couché",
        description="Barre abaissée à la poitrine puis poussée verticale.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.PECTORAUX, MuscleGroup.TRICEPS),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="barre",
        estimated_duration=15,
    ),
    ExerciseSeedDefinition(
        name="Tirage vertical",
        description="Traction vers le haut en pronation ou neutre à la poulie.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.DOS, MuscleGroup.BICEPS),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="machine",
        estimated_duration=12,
    ),
    ExerciseSeedDefinition(
        name="Soulevé de terre roumain",
        description="Hanche en flexion avec jambes semi-fléchies, dos neutre.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.FESSIERS, MuscleGroup.DOS, MuscleGroup.JAMBES),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="halteres",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Presse à cuisses",
        description="Poussée guidée des jambes, amplitude complète contrôlée.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.FESSIERS),
        difficulty=Difficulty.DEBUTANT,
        equipment="machine",
        estimated_duration=12,
    ),
    ExerciseSeedDefinition(
        name="Développé militaire",
        description="Poussée verticale depuis les épaules, buste stable.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.EPAULES, MuscleGroup.TRICEPS),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="halteres",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Curl biceps",
        description="Flexion des coudes en supination, contrôle en descente.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.BICEPS, MuscleGroup.AVANT_BRAS),
        difficulty=Difficulty.DEBUTANT,
        equipment="halteres",
        estimated_duration=8,
    ),
    ExerciseSeedDefinition(
        name="Extension triceps à la poulie",
        description="Extension des avant-bras depuis coude fixe, câble haut.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.TRICEPS,),
        difficulty=Difficulty.DEBUTANT,
        equipment="machine",
        estimated_duration=8,
    ),
    ExerciseSeedDefinition(
        name="Leg curl allongé",
        description="Flexion des ischio-jambiers sur machine couche.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.JAMBES,),
        difficulty=Difficulty.DEBUTANT,
        equipment="machine",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Leg extension",
        description="Extension des genoux assis, quadriceps isolé.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.JAMBES,),
        difficulty=Difficulty.DEBUTANT,
        equipment="machine",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Écarté à la machine",
        description="Adduction des bras sur le plan horizontal, poitrine contractée.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.PECTORAUX,),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="machine",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Rowing haltère",
        description="Tirage d'une haltère vers la hanche, dos plat.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.DOS, MuscleGroup.BICEPS),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="halteres",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Gainage latéral",
        description="Maintien sur un avant-bras, hanches alignées.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.ABDOS, MuscleGroup.EPAULES),
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=2,
    ),
    ExerciseSeedDefinition(
        name="Mountain climbers",
        description="Alternance rapide des genoux vers la poitrine en planche.",
        exercise_type=ExerciseType.CARDIO,
        muscle_groups=(MuscleGroup.ABDOS, MuscleGroup.JAMBES, MuscleGroup.EPAULES),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="poids_du_corps",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Jumping jacks",
        description="Sauts en écartant jambes et bras au-dessus de la tête.",
        exercise_type=ExerciseType.CARDIO,
        muscle_groups=(MuscleGroup.CORPS_ENTIER,),
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Étirement ischio-jambiers debout",
        description="Flexion avant du buste jambe tendue sur support.",
        exercise_type=ExerciseType.SOUPLESSE,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.DOS),
        difficulty=Difficulty.DEBUTANT,
        equipment="none",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Étirement poitrine au mur",
        description="Bras en abduction contre un angle, ouverture thoracique.",
        exercise_type=ExerciseType.SOUPLESSE,
        muscle_groups=(MuscleGroup.PECTORAUX, MuscleGroup.EPAULES),
        difficulty=Difficulty.DEBUTANT,
        equipment="none",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Chien tête en bas",
        description="Flexion hanche mains au sol, bassin vers le ciel.",
        exercise_type=ExerciseType.SOUPLESSE,
        muscle_groups=(MuscleGroup.DOS, MuscleGroup.JAMBES),
        difficulty=Difficulty.DEBUTANT,
        equipment="poids_du_corps",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Kettlebell swing",
        description="Bascule hanche avec kettlebell à hauteur d'épaules.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.FESSIERS, MuscleGroup.DOS, MuscleGroup.JAMBES),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="kettlebell",
        estimated_duration=8,
    ),
    ExerciseSeedDefinition(
        name="Step-up",
        description="Montée sur banc une jambe à la fois, contrôle de la descente.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.FESSIERS),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="banc",
        estimated_duration=10,
    ),
    ExerciseSeedDefinition(
        name="Planche dynamique",
        description="Alternance bras tendus et avant-bras sans hausser les hanches.",
        exercise_type=ExerciseType.FORCE,
        muscle_groups=(MuscleGroup.ABDOS, MuscleGroup.PECTORAUX, MuscleGroup.EPAULES),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="poids_du_corps",
        estimated_duration=5,
    ),
    ExerciseSeedDefinition(
        name="Vélo elliptique",
        description="Mouvement elliptique continu, résistance modérée.",
        exercise_type=ExerciseType.CARDIO,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.FESSIERS),
        difficulty=Difficulty.DEBUTANT,
        equipment="machine",
        estimated_duration=20,
    ),
    ExerciseSeedDefinition(
        name="Natation crawl",
        description="Nage frontale alternée, rotation du buste et battements pieds.",
        exercise_type=ExerciseType.ENDURANCE,
        muscle_groups=(MuscleGroup.DOS, MuscleGroup.PECTORAUX, MuscleGroup.EPAULES),
        difficulty=Difficulty.INTERMEDIAIRE,
        equipment="piscine",
        estimated_duration=30,
    ),
    ExerciseSeedDefinition(
        name="Marche rapide",
        description="Allure soutenue bras actifs, posture droite.",
        exercise_type=ExerciseType.ENDURANCE,
        muscle_groups=(MuscleGroup.JAMBES, MuscleGroup.FESSIERS),
        difficulty=Difficulty.DEBUTANT,
        equipment="none",
        estimated_duration=30,
    ),
)


def build_default_exercises(
    dt: DateTimeService,
    uuid_gen: UUIDGenerator,
) -> list[Exercise]:
    """Construit les agrégats `Exercise` pour le seed (nouveaux UUID à chaque appel)."""
    now = dt.utcnow()
    return [
        Exercise(
            id=uuid_gen.next(),
            name=definition.name,
            description=definition.description,
            exercise_type=definition.exercise_type,
            muscle_groups=list(definition.muscle_groups),
            difficulty=definition.difficulty,
            equipment=definition.equipment,
            estimated_duration=definition.estimated_duration,
            created_at=now,
            updated_at=now,
        )
        for definition in DEFAULT_EXERCISE_DEFINITIONS
    ]
