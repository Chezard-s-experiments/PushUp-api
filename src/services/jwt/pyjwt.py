from datetime import timedelta
from typing import Any

from injection import injectable
from jwt import PyJWT

from src.services.datetime.abc import DateTimeService
from src.services.jwt.abc import JWTService
from src.settings import Settings


class PyJWTService(JWTService):
    def __init__(
        self,
        datetime: DateTimeService,
        secret_key: str,
        algorithm: str = "HS256",
        verify_expiration: bool = True,
    ) -> None:
        self.__algorithm = algorithm
        self.__datetime = datetime
        self.__internal = PyJWT({"verify_exp": verify_expiration})
        self.__secret_key = secret_key

    def decode(self, token: str) -> dict[str, Any]:
        return self.__internal.decode(
            token,
            algorithms=[self.__algorithm],
            key=self.__secret_key,
        )

    def encode(self, payload: dict[str, Any], lifespan: timedelta | None = None) -> str:
        payload = payload.copy()

        if lifespan:
            payload["exp"] = self.__datetime.utcnow() + lifespan

        return self.__internal.encode(
            payload=payload,
            algorithm=self.__algorithm,
            key=self.__secret_key,
        )


@injectable(on=JWTService)
def _pyjwt_service_recipe(
    datetime: DateTimeService,
    settings: Settings,
) -> PyJWTService:  # pragma: no cover
    secret_key = settings.secret_key.get_secret_value()
    return PyJWTService(datetime, secret_key)
