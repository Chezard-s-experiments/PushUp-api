from typing import Annotated
from uuid import UUID

from cq import CommandBus, QueryBus
from fastapi import APIRouter, Depends, HTTPException, status
from injection.ext.fastapi import Inject
from pydantic import BaseModel, EmailStr

from src.core.auth.commands.login_user import LoginUserCommand
from src.core.auth.commands.login_with_oauth import LoginWithOAuthCommand
from src.core.auth.commands.refresh_token import RefreshTokenCommand
from src.core.auth.dtos.tokens import AccessTokenPayload
from src.core.users.aggregates import User
from src.core.users.commands.register_user import RegisterUserCommand
from src.core.users.queries.get_user_profile import (
    GetUserProfileQuery,
    UserProfileView,
)
from src.infra.api.dependencies import get_claimant_id
from src.services.jwt.abc import JWTService

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None


class RefreshPayload(BaseModel):
    refresh_token: str


class OAuthLoginPayload(BaseModel):
    token: str


class AuthWithUserResponse(BaseModel):
    token: AccessTokenPayload
    user: UserProfileView


@router.post(
    "/register",
    operation_id="Register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthWithUserResponse,
)
async def register(
    payload: RegisterPayload,
    command_bus: Inject[CommandBus[User]],
    jwt: Inject[JWTService],
) -> AuthWithUserResponse:
    from src.core.auth.commands.login_user import (
        ACCESS_TOKEN_LIFESPAN,
        REFRESH_TOKEN_LIFESPAN,
    )

    command = RegisterUserCommand(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    user = await command_bus.dispatch(command)

    claims = {"user_id": str(user.id), "email": str(user.email)}

    access_token = jwt.encode(
        {**claims, "type": "access"},
        lifespan=ACCESS_TOKEN_LIFESPAN,
    )
    refresh_token = jwt.encode(
        {**claims, "type": "refresh"},
        lifespan=REFRESH_TOKEN_LIFESPAN,
    )

    return AuthWithUserResponse(
        token=AccessTokenPayload(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        user=UserProfileView.model_validate(user.to_public_dict()),
    )


@router.post(
    "/login",
    operation_id="Login",
    response_model=AuthWithUserResponse,
)
async def login(
    payload: LoginPayload,
    command_bus: Inject[CommandBus[AccessTokenPayload]],
    query_bus: Inject[QueryBus[UserProfileView | None]],
    jwt: Inject[JWTService],
) -> AuthWithUserResponse:
    command = LoginUserCommand(
        email=payload.email,
        password=payload.password,
    )
    token = await command_bus.dispatch(command)

    decoded = jwt.decode(token.access_token)
    user_id = UUID(decoded["user_id"])

    query = GetUserProfileQuery(user_id=user_id)
    view = await query_bus.dispatch(query)

    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return AuthWithUserResponse(token=token, user=view)


@router.post(
    "/refresh",
    operation_id="RefreshToken",
    response_model=AccessTokenPayload,
)
async def refresh(
    payload: RefreshPayload,
    command_bus: Inject[CommandBus[AccessTokenPayload]],
) -> AccessTokenPayload:
    command = RefreshTokenCommand(refresh_token=payload.refresh_token)
    return await command_bus.dispatch(command)


@router.get("/me", operation_id="GetCurrentUser", response_model=UserProfileView)
async def get_current_user(
    claimant_id: Annotated[UUID, Depends(get_claimant_id)],
    query_bus: Inject[QueryBus[UserProfileView | None]],
) -> UserProfileView:
    query = GetUserProfileQuery(user_id=claimant_id)
    view = await query_bus.dispatch(query)

    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return view


@router.post(
    "/oauth",
    operation_id="LoginWithOAuth",
    response_model=AuthWithUserResponse,
)
async def login_with_oauth(
    payload: OAuthLoginPayload,
    command_bus: Inject[CommandBus[AccessTokenPayload]],
    query_bus: Inject[QueryBus[UserProfileView | None]],
    jwt: Inject[JWTService],
) -> AuthWithUserResponse:
    command = LoginWithOAuthCommand(
        # Pour l'instant on ne supporte que Google côté infra.
        provider="google",
        token=payload.token,
    )
    token = await command_bus.dispatch(command)

    decoded = jwt.decode(token.access_token)
    user_id = UUID(decoded["user_id"])

    query = GetUserProfileQuery(user_id=user_id)
    view = await query_bus.dispatch(query)

    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return AuthWithUserResponse(token=token, user=view)
