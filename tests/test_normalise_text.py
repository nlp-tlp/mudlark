import pytest
from mudlark import normalise_text


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("BROKEN", "broken"),  # uppercase
        ("replace   pump", "replace pump"),  # extra spaces
        ("X/X", "x / x"),  # space around slashes
        ("glass", "glass"),  # double s endings
        ("slurries", "slurry"),  # ies > ry
        ("boxes", "box"),  # xes -> x
        ("pumps busted", "pump busted"),  # pluralisation
        ("enGiNe was broken", "engine is broken"),  # present tense
        ("a leak was Formed", "a leak is formed"),  # present tense
    ],
)
def test_normalise_text_default(test_input, expected):
    """Ensure the normalise_text function works as expected.
    At the moment, this always uses simple_normalise().

    Args:
        test_input (TYPE): Description
        expected (TYPE): Description
    """
    assert normalise_text(test_input) == expected
