from src.core.users.value_objects import HashedPassword
from src.services.hasher.argon2 import Argon2Hasher


def test_from_hash_accepts_any_string() -> None:
    hashed = HashedPassword.from_hash("$argon2id$v=19$m=65536,t=3,p=4$fake$salt")
    assert hashed.get_secret_value() == "$argon2id$v=19$m=65536,t=3,p=4$fake$salt"


def test_verify_returns_true_when_password_matches() -> None:
    hasher = Argon2Hasher()
    hashed = HashedPassword.from_hash(hasher.hash("s3cret!"))
    assert hashed.verify("s3cret!", hasher) is True


def test_verify_returns_false_when_password_does_not_match() -> None:
    hasher = Argon2Hasher()
    hashed = HashedPassword.from_hash(hasher.hash("s3cret!"))
    assert hashed.verify("wrong", hasher) is False


def test_hash_is_irreversible() -> None:
    """Le hash ne permet pas de retrouver le mot de passe en clair."""
    hasher = Argon2Hasher()
    plain = "my-password"
    hashed = HashedPassword.from_hash(hasher.hash(plain))
    # On ne peut que vérifier, pas extraire
    assert hashed.get_secret_value() != plain
    assert hashed.verify(plain, hasher) is True
