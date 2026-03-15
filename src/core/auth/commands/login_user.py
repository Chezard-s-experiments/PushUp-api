from datetime import timedelta
from typing import NamedTuple

from cq import command_handler
from pydantic import BaseModel, EmailStr, SecretStr

from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.auth.exceptions import InvalidCredentialsError
from src.core.users.ports.repo import UserRepository
from src.core.users.value_objects import HashedPassword
from src.services.datetime.abc import DateTimeService
from src.services.hasher.abc import Hasher
from src.services.jwt.abc import JWTService

ACCESS_TOKEN_LIFESPAN = timedelta(hours=1)
REFRESH_TOKEN_LIFESPAN = timedelta(days=7)


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

        if not user.hashed_password.verify(password, self.hasher):
            raise InvalidCredentialsError()

        if user.hashed_password.needs_rehash(self.hasher):
            updated_user = user.model_copy(
                update={
                    "hashed_password": HashedPassword.from_hash(
                        self.hasher.hash(password)
                    ),
                    "updated_at": self.datetime.utcnow(),
                }
            )
            await self.repo.update(updated_user)

        claims = {"user_id": str(user.id), "email": str(user.email)}

        access_token = self.jwt.encode(
            {**claims, "type": "access"},
            lifespan=ACCESS_TOKEN_LIFESPAN,
        )
        refresh_token = self.jwt.encode(
            {**claims, "type": "refresh"},
            lifespan=REFRESH_TOKEN_LIFESPAN,
        )

        return AccessTokenPayload(
            access_token=access_token,
            refresh_token=refresh_token,
        )
