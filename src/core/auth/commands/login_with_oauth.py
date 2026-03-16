from datetime import timedelta
from typing import NamedTuple
from uuid import uuid4

from cq import command_handler
from pydantic import BaseModel, SecretStr

from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.auth.ports.oauth_verifier import OAuthUserInfo, OAuthVerifier
from src.core.users.aggregates import User
from src.core.users.ports.repo import UserRepository
from src.core.users.value_objects import Email, HashedPassword, OAuthProvider
from src.services.datetime.abc import DateTimeService
from src.services.hasher.abc import Hasher
from src.services.jwt.abc import JWTService
from src.services.uuid.abc import UUIDGenerator

ACCESS_TOKEN_LIFESPAN = timedelta(hours=1)
REFRESH_TOKEN_LIFESPAN = timedelta(days=7)


class LoginWithOAuthCommand(BaseModel):
    provider: OAuthProvider
    token: SecretStr


@command_handler
class LoginWithOAuthHandler(NamedTuple):
    datetime: DateTimeService
    hasher: Hasher
    jwt: JWTService
    repo: UserRepository
    uuid: UUIDGenerator
    verifier: OAuthVerifier

    async def handle(self, command: LoginWithOAuthCommand) -> AccessTokenPayload:
        info: OAuthUserInfo = await self.verifier.verify(
            provider=command.provider,
            token=command.token.get_secret_value(),
        )

        user = await self.repo.get_by_email(info.email)

        now = self.datetime.utcnow()

        if user is None:
            # Génère un mot de passe aléatoire uniquement pour satisfaire les contraintes
            # de persistance. L'utilisateur ne l'utilise pas directement.
            random_password = uuid4().hex
            hashed_password = HashedPassword.from_hash(
                self.hasher.hash(random_password)
            )

            user = User(
                id=self.uuid.next(),
                email=Email(info.email),
                hashed_password=hashed_password,
                first_name=info.first_name,
                last_name=info.last_name,
                oauth_provider=command.provider,
                oauth_id=info.provider_user_id,
                created_at=now,
                updated_at=now,
            )
            await self.repo.add(user)
        else:
            updated_user = user.model_copy(
                update={
                    "oauth_provider": command.provider,
                    "oauth_id": info.provider_user_id,
                    "first_name": user.first_name or info.first_name,
                    "last_name": user.last_name or info.last_name,
                    "updated_at": now,
                }
            )
            await self.repo.update(updated_user)
            user = updated_user

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
