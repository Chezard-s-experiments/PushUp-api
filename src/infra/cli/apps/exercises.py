from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typer import Typer, echo, style

from src.core.exercises.seed_data import build_default_exercises
from src.infra.adapters.exercises.repo import SQLAExerciseRepository
from src.infra.entrypoint import main
from src.services.datetime.std import StdDateTimeService
from src.services.uuid.ulid import ULIDGenerator
from src.settings import Settings

app = Typer(name="exercises")


@app.command("seed-defaults")
def seed_defaults() -> None:
    """Charge les 30 exercices par défaut (upsert par nom, idempotent)."""

    @main(autocall=True)
    async def _(settings: Settings) -> None:
        engine = create_async_engine(settings.db.get_url())
        datetime_svc = StdDateTimeService()
        uuid_gen = ULIDGenerator()
        exercises = build_default_exercises(datetime_svc, uuid_gen)
        async with AsyncSession(engine) as session:
            async with session.begin():
                repo = SQLAExerciseRepository(session=session)
                await repo.upsert_many(exercises)
        await engine.dispose()
        echo(
            style(
                f"{len(exercises)} exercices ont été insérés ou mis à jour.",
                fg="green",
                bold=True,
            ),
        )
