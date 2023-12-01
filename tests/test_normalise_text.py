"""Tests for the normalise_text function."""
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

        ("Test Tube", "test tube"), # 1. Lowercase text
        ("test-tube", "test - tube"), # 2. Add space around hypen
        ("test,tube", "test tube"), # 3. Remove commas
        ("a/c leakin", "air conditioner leak"), # 4. fix typos 
        ("test/tube", "test / tube"), # 5. Add space around slash
        ("check ABX32ad and DDdkL204ddd", "check AssetID and AssetID"), # 6. Anonymise sentence
        ("  test     tube   and   test  ", "test tube and test"), # 7. Remove extra spaces
        ("metal pipe was broken", "metal pipe is broken") # 9. Align tense 
        # ("the glasses holds foxes and has holes", "the glasse hold fox and has hole") # 10. Pluralise 


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
