from cq import CommandBus
from fastapi import APIRouter
from injection.ext.fastapi import Inject
from pydantic import BaseModel, EmailStr

from src.core.auth.commands.login_user import LoginUserCommand
from src.core.auth.dtos.tokens import AccessTokenPayload

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


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
