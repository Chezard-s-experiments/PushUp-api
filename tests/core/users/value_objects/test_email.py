import pytest
from pydantic import ValidationError

from src.core.users.value_objects import Email


def test_email_accepts_valid_format() -> None:
    email = Email("user@example.com")
    assert str(email) == "user@example.com"


def test_email_rejects_invalid_format() -> None:
    with pytest.raises(ValidationError):
        Email("not-an-email")


def test_email_equality() -> None:
    assert Email("a@b.co") == Email("a@b.co")
    assert Email("a@b.co") != Email("other@b.co")
