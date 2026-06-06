import pytest

from src.infra.api.dependencies import _parse_accept_language


@pytest.mark.parametrize(
    ("header", "expected_language"),
    [
        ("fr-FR", "fr"),
        ("fr_FR", "fr"),
        ("fr-FR,fr;q=0.9,en-US;q=0.8", "fr"),
        ("en-US,en;q=0.5", "en"),
        ("fr", "fr"),
        ("*", None),
        ("invalid", None),
        ("x-default", None),
        ("", None),
    ],
)
def test_parse_accept_language(header: str, expected_language: str | None) -> None:
    locale = _parse_accept_language(header)

    if expected_language is None:
        assert locale is None
    else:
        assert locale is not None
        assert locale.language == expected_language
