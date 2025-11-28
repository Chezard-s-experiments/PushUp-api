from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Annotated, Self

from babel import Locale
from fastapi import APIRouter, Depends, FastAPI, Request, Response, status
from fastapi.exceptions import ValidationException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from injection import MappedScope, injectable
from jwt import InvalidTokenError
from pydantic import ValidationError

from src.enums import Scope
from src.exceptions import ApplicationError
from src.infra.api.dependencies import get_locale
from src.infra.entrypoint import lifespan
from src.settings import Settings


@injectable
@dataclass(frozen=True)
class FastAPIBuilder:
    settings: Settings
    routers: list[APIRouter] = field(default_factory=list, init=False)

    def build(self) -> FastAPI:
        settings = self.settings
        debug = settings.debug
        app = FastAPI(
            debug=debug,
            dependencies=[Depends(_request_scope)],
            lifespan=lambda _: lifespan(settings.profile),
            **{} if debug else {"openapi_url": None},  # type: ignore[arg-type]
        )

        for router in self.routers:
            app.include_router(router)

        app.add_middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_headers=["*"],
            allow_methods=["*"],
            allow_origins=settings.allowed_hosts,
        )

        @app.exception_handler(ApplicationError)
        async def _(request: Request, exception: ApplicationError) -> Response:
            return ORJSONResponse(
                status_code=exception.http_status,
                content=exception.dump(),
            )

        @app.exception_handler(InvalidTokenError)
        async def _(request: Request, exception: InvalidTokenError) -> Response:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)

        @app.exception_handler(ValidationError)
        async def _(request: Request, exception: ValidationError) -> Response:
            return ORJSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "errors": exception.errors(
                        include_url=False,
                        include_context=True,
                        include_input=False,
                    )
                },
            )

        @app.exception_handler(ValidationException)
        async def _(request: Request, exception: ValidationException) -> Response:
            return ORJSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"errors": exception.errors()},
            )

        return app

    def include_routers(self, *routers: APIRouter) -> Self:
        self.routers.extend(routers)
        return self


@dataclass(frozen=True)
class _RequestBindings:
    locale: Locale | None = field(default=None)

    scope = MappedScope(Scope.REQUEST)


async def _request_scope(
    locale: Annotated[Locale | None, Depends(get_locale)],
) -> AsyncIterator[None]:
    async with _RequestBindings(locale).scope.adefine():
        yield
