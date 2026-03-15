"""Construction de l'app FastAPI (utilisé par main et par les tests d'intégration)."""

from fastapi import FastAPI

from src.infra.api.builder import FastAPIBuilder
from src.infra.api.routes import auth, exercises, health
from src.settings import Settings


def build_app(settings: Settings) -> FastAPI:
    """Construit l'app FastAPI avec les routers et la config donnée."""
    return (
        FastAPIBuilder(settings=settings)
        .include_routers(
            health.router,
            auth.router,
            exercises.router,
        )
        .build()
    )
