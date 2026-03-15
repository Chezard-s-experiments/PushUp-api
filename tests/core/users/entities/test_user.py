"""Tests unitaires sur l'entité User."""

from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.core.users.aggregates import User
from src.core.users.value_objects import Email, HashedPassword


def _make_hashed_password() -> HashedPassword:
    return HashedPassword.from_hash(
        "$argon2id$v=19$m=65536,t=3,p=4$fakesalt$fakehash"
    )


def test_user_creation_with_required_fields() -> None:
    now = datetime(2025, 1, 15, tzinfo=UTC)
    user = User(
        id=UUID(int=1),
        email=Email("alice@example.com"),
        hashed_password=_make_hashed_password(),
        created_at=now,
        updated_at=now,
    )
    assert user.id == UUID(int=1)
    assert str(user.email) == "alice@example.com"
    assert user.first_name is None
    assert user.last_name is None
    assert user.created_at == now
    assert user.updated_at == now


def test_user_creation_with_optional_names() -> None:
    now = datetime(2025, 1, 15, tzinfo=UTC)
    user = User(
        id=UUID(int=2),
        email=Email("bob@example.com"),
        hashed_password=_make_hashed_password(),
        first_name="Bob",
        last_name="Martin",
        created_at=now,
        updated_at=now,
    )
    assert user.first_name == "Bob"
    assert user.last_name == "Martin"


def test_to_public_dict_includes_expected_fields() -> None:
    now = datetime(2025, 1, 15, tzinfo=UTC)
    user = User(
        id=UUID(int=1),
        email=Email("alice@example.com"),
        hashed_password=_make_hashed_password(),
        created_at=now,
        updated_at=now,
    )
    public = user.to_public_dict()
    assert public["id"] == UUID(int=1)
    assert public["email"] == "alice@example.com"
    assert public["first_name"] is None
    assert public["last_name"] is None
    assert public["created_at"] == now
    assert public["updated_at"] == now


def test_to_public_dict_does_not_expose_hashed_password() -> None:
    """Le mot de passe hashé ne doit jamais apparaître dans la représentation publique."""
    now = datetime(2025, 1, 15, tzinfo=UTC)
    user = User(
        id=UUID(int=1),
        email=Email("alice@example.com"),
        hashed_password=_make_hashed_password(),
        created_at=now,
        updated_at=now,
    )
    public = user.to_public_dict()
    assert "hashed_password" not in public
    assert "password" not in public


def test_user_rejects_invalid_email() -> None:
    now = datetime(2025, 1, 15, tzinfo=UTC)
    with pytest.raises(ValidationError):
        User(
            id=UUID(int=1),
            email="not-an-email",
            hashed_password=_make_hashed_password(),
            created_at=now,
            updated_at=now,
        )


def test_user_requires_email_as_vo() -> None:
    """L'email doit être un Email (VO), pas une chaîne brute."""
    now = datetime(2025, 1, 15, tzinfo=UTC)
    user = User(
        id=UUID(int=1),
        email=Email("alice@example.com"),
        hashed_password=_make_hashed_password(),
        created_at=now,
        updated_at=now,
    )
    assert isinstance(user.email, Email)
    assert str(user.email) == "alice@example.com"
