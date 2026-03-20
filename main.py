from injection import get_instance

from src.infra.api.builder import FastAPIBuilder
from src.infra.api.routes import auth, exercises, health
from src.infra.cli.apps import db, exercises as exercises_cli
from src.infra.cli.builder import TyperBuilder

if __name__ == "__main__":
    cli = (
        get_instance(TyperBuilder)
        .include_apps(
            db.app,
            exercises_cli.app,
        )
        .build()
    )
    cli()

else:
    app = (
        get_instance(FastAPIBuilder)
        .include_routers(
            health.router,
            auth.router,
            exercises.router,
        )
        .build()
    )
