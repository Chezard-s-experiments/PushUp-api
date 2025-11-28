from injection import get_instance

from src.infra.api.builder import FastAPIBuilder
from src.infra.api.routes import auth, exercises, users
from src.infra.cli.apps import db
from src.infra.cli.builder import TyperBuilder

if __name__ == "__main__":
    cli = (
        get_instance(TyperBuilder)
        .include_apps(
            db.app,
        )
        .build()
    )
    cli()

else:
    app = (
        get_instance(FastAPIBuilder)
        .include_routers(
            auth.router,
            users.router,
            exercises.router,
        )
        .build()
    )
