from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture
def client(test_client: AsyncClient) -> AsyncClient:
    """Alias lisible pour le client HTTP de test."""
    return test_client


async def _register_and_get_token_and_user(
    client: AsyncClient,
    email: str | None = None,
    password: str = "s3cret!",
) -> dict[str, Any]:
    effective_email = email or f"user-{uuid4().hex}@example.com"

    response = await client.post(
        "/auth/register",
        json={"email": effective_email, "password": password},
    )
    assert response.status_code == 201
    data = response.json()

    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == effective_email

    return data


@pytest.mark.asyncio()
async def test_register_returns_token_and_user(client: AsyncClient) -> None:
    data = await _register_and_get_token_and_user(client)

    assert data["token"]["access_token"]
    assert data["token"]["refresh_token"]
    assert data["token"]["token_type"] == "bearer"


@pytest.mark.asyncio()
async def test_login_returns_token_and_user(client: AsyncClient) -> None:
    email = f"login-{uuid4().hex}@example.com"
    await _register_and_get_token_and_user(client, email=email)

    response = await client.post(
        "/auth/login",
        json={"email": email, "password": "s3cret!"},
    )
    assert response.status_code == 200
    data = response.json()

    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == email
    assert data["token"]["access_token"]
    assert data["token"]["refresh_token"]


@pytest.mark.asyncio()
async def test_refresh_returns_new_tokens(client: AsyncClient) -> None:
    data = await _register_and_get_token_and_user(client)
    refresh_token = data["token"]["refresh_token"]

    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    tokens = response.json()

    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio()
async def test_refresh_with_access_token_returns_401(client: AsyncClient) -> None:
    data = await _register_and_get_token_and_user(client)
    access_token = data["token"]["access_token"]

    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_refresh_with_invalid_token_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_me_returns_user_when_authenticated(client: AsyncClient) -> None:
    email = f"me-{uuid4().hex}@example.com"
    data = await _register_and_get_token_and_user(client, email=email)
    token = data["token"]["access_token"]

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    me = response.json()

    assert me["email"] == data["user"]["email"]


@pytest.mark.asyncio()
async def test_me_unauthorized_without_token(client: AsyncClient) -> None:
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio()
async def test_me_rejects_refresh_token(client: AsyncClient) -> None:
    data = await _register_and_get_token_and_user(client)
    refresh_token = data["token"]["refresh_token"]

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 401
