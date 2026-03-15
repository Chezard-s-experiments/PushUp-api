"""Tests d'intégration sur SQLAUserRepository (base réelle)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.users.aggregates import User
from src.core.users.ports.repo import UserRepository
from src.core.users.value_objects import Email, HashedPassword
from src.infra.adapters.users.repo import SQLAUserRepository


def _make_user(
    *,
    email: str = "alice@example.com",
    password_hash: str = "$argon2id$v=19$m=65536,t=3,p=4$fakesalt$fakehash",
) -> User:
    now = datetime(2025, 1, 15, tzinfo=UTC)
    return User(
        id=uuid4(),
        email=Email(email),
        hashed_password=HashedPassword.from_hash(password_hash),
        first_name="Alice",
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_add_and_get_by_id(db_session: AsyncSession) -> None:
    """Après add, get_by_id retrouve l'utilisateur."""
    repo: UserRepository = SQLAUserRepository(session=db_session)
    user = _make_user(email="add-get@example.com")

    await repo.add(user)
    found = await repo.get_by_id(user.id)

    assert found is not None
    assert found.id == user.id
    assert str(found.email) == str(user.email)
    assert found.first_name == user.first_name
    assert found.last_name == user.last_name
    assert (
        found.hashed_password.get_secret_value()
        == user.hashed_password.get_secret_value()
    )


@pytest.mark.asyncio
async def test_add_and_get_by_email(db_session: AsyncSession) -> None:
    """Après add, get_by_email retrouve l'utilisateur."""
    repo: UserRepository = SQLAUserRepository(session=db_session)
    user = _make_user(email="by-email@example.com")

    await repo.add(user)
    found = await repo.get_by_email("by-email@example.com")

    assert found is not None
    assert found.id == user.id
    assert str(found.email) == "by-email@example.com"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_absent(db_session: AsyncSession) -> None:
    """get_by_id retourne None si l'utilisateur n'existe pas."""
    repo: UserRepository = SQLAUserRepository(session=db_session)
    found = await repo.get_by_id(uuid4())
    assert found is None


@pytest.mark.asyncio
async def test_get_by_email_returns_none_when_absent(db_session: AsyncSession) -> None:
    """get_by_email retourne None si l'utilisateur n'existe pas."""
    repo: UserRepository = SQLAUserRepository(session=db_session)
    found = await repo.get_by_email("absent@example.com")
    assert found is None


@pytest.mark.asyncio
async def test_update_persists_changes(db_session: AsyncSession) -> None:
    """update modifie l'utilisateur en base."""
    repo: UserRepository = SQLAUserRepository(session=db_session)
    user = _make_user(email="update@example.com")
    await repo.add(user)

    updated = user.model_copy(
        update={
            "first_name": "Updated",
            "last_name": "Name",
            "updated_at": datetime(2025, 2, 1, tzinfo=UTC),
        }
    )
    await repo.update(updated)

    found = await repo.get_by_id(user.id)
    assert found is not None
    assert found.first_name == "Updated"
    assert found.last_name == "Name"


@pytest.mark.asyncio
async def test_unique_email_constraint(db_session: AsyncSession) -> None:
    """Deux utilisateurs avec le même email violent la contrainte d'unicité."""
    repo: UserRepository = SQLAUserRepository(session=db_session)
    user1 = _make_user(email="unique@example.com")
    user2 = _make_user(email="unique@example.com")
    user2 = user2.model_copy(update={"id": uuid4()})

    await repo.add(user1)

    with pytest.raises(IntegrityError):
        await repo.add(user2)
