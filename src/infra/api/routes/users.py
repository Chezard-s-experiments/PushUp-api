from typing import Annotated
from uuid import UUID

from cq import CommandBus, QueryBus
from fastapi import APIRouter, Depends, HTTPException, status
from injection.ext.fastapi import Inject
from pydantic import BaseModel, EmailStr

from src.core.users.aggregates import User
from src.core.users.commands.register_user import RegisterUserCommand
from src.core.users.dtos import UserRead
from src.core.users.queries.get_user_profile import (
    GetUserProfileQuery,
    UserProfileView,
)
from src.infra.api.dependencies import get_claimant_id

router = APIRouter(prefix="/users", tags=["Users"])


class RegisterUserPayload(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register_user(
    payload: RegisterUserPayload,
    command_bus: Inject[CommandBus[User]],
) -> UserRead:
    command = RegisterUserCommand(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    user = await command_bus.dispatch(command)
    return UserRead.model_validate(user.to_public_dict())


@router.get("/me", response_model=UserProfileView)
async def get_me(
    claimant_id: Annotated[UUID, Depends(get_claimant_id)],
    query_bus: Inject[QueryBus[UserProfileView | None]],
) -> UserProfileView:
    query = GetUserProfileQuery(user_id=claimant_id)
    view = await query_bus.dispatch(query)

    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return view
