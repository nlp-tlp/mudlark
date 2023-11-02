import pytest
from mudlark import normalise_text


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("BROKEN", "broken"),
        ("replace   pump", "replace pump"),
        ("X/X", "x / x"),
    ],
)
def test_normalise_text_default(test_input, expected):
    assert normalise_text(test_input) == expected
