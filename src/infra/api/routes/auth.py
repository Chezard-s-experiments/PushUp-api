from datetime import timedelta
from typing import Annotated
from uuid import UUID

from cq import CommandBus, QueryBus
from fastapi import APIRouter, Depends, HTTPException, status
from injection.ext.fastapi import Inject
from pydantic import BaseModel, EmailStr

from src.core.auth.commands.login_user import LoginUserCommand
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
    command = RegisterUserCommand(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    user = await command_bus.dispatch(command)

    access_token = jwt.encode(
        {"user_id": str(user.id), "email": str(user.email)},
        lifespan=timedelta(hours=1),
    )

    return AuthWithUserResponse(
        token=AccessTokenPayload(access_token=access_token),
        user=UserProfileView.model_validate(user.to_public_dict()),
    )


@router.post("/login", operation_id="Login", response_model=AccessTokenPayload)
async def login(
    payload: LoginPayload,
    command_bus: Inject[CommandBus[AccessTokenPayload]],
) -> AccessTokenPayload:
    command = LoginUserCommand(
        email=payload.email,
        password=payload.password,
    )
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
