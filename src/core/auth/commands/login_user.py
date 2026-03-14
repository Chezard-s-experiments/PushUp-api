from datetime import timedelta
from typing import NamedTuple

from cq import command_handler
from pydantic import BaseModel, EmailStr, SecretStr

from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.auth.exceptions import InvalidCredentialsError
from src.core.users.ports.repo import UserRepository
from src.services.datetime.abc import DateTimeService
from src.services.hasher.abc import Hasher
from src.services.jwt.abc import JWTService


class LoginUserCommand(BaseModel):
    email: EmailStr
    password: SecretStr


@command_handler
class LoginUserHandler(NamedTuple):
    datetime: DateTimeService
    hasher: Hasher
    jwt: JWTService
    repo: UserRepository

    async def handle(self, command: LoginUserCommand) -> AccessTokenPayload:
        user = await self.repo.get_by_email(command.email)

        if user is None:
            raise InvalidCredentialsError()

        password = command.password.get_secret_value()
        hashed_password = user.hashed_password.get_secret_value()

        if not self.hasher.verify(password, hashed_password):
            raise InvalidCredentialsError()

        if self.hasher.needs_rehash(hashed_password):
            updated_user = user.model_copy(
                update={
                    "hashed_password": SecretStr(self.hasher.hash(password)),
                    "updated_at": self.datetime.utcnow(),
                }
            )
            await self.repo.update(updated_user)

        token = self.jwt.encode(
            {"user_id": str(user.id), "email": str(user.email)},
            lifespan=timedelta(hours=1),
        )

        return AccessTokenPayload(access_token=token)
