"""Tests for the normalise_text function."""
import pytest
from mudlark import normalise_text


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # [1] Test cases for converting text to lowercase
        ("UpperCase", "uppercase"),
        ("MixedCaSe", "mixedcase"),
        ("BROKEN", "broken"),
        ("Test Tube", "test tube"),
        
        # [2] Test cases for adding spaces around hyphens
        ("test-tube", "test - tube"),
        ("word-hyphen-word", "word - hyphen - word"),
        
        # [3] Test cases for removing commas
        ("test,tube", "test tube"),
        ("engine,pump,pipe", "engine pump pipe"),
        
        # [4] Test cases for fixing typos
        ("a/c leakin", "air conditioner leak"),
        ("accum boken", "accumulator broken"),
        ("conmon", "condition monitoring"),
        ("wtp reapair and repalce", "water treatment pump repair and replace"),
        ("gw innadequate", "gland water inadequate"),
        # ("PLC", "programmable logic controller"),   # ! csv file should be lower case plc
        # ("ROM", "run of mine"),                     # ! csv file should be lower case rom
        # ("BFWP", "boiler feed water pump"),         # ! csv file should be lower case bfwp
        # ("air / con", "air / con"),   # ! csv file ?
        # ("air - con", "air - con"),   # ! csv file ?
        
        # [5] Test cases for adding spaces around slashes
        ("X/X", "x / x"),
        ("test/tube", "test / tube"),
        
        # [6] Test cases for anonymising sentences
        ("check ABX32ad and DDdkL204ddd", "check AssetID and AssetID"),
        ("AB123 XYZ789", "AssetID AssetID"),
        ("nothing here", "nothing here"),
        ("XY345Z", "AssetID"),
        
        # [7] Test cases for removing extra spaces
        ("replace   pump", "replace pump"),
        ("  test     tube   and   test  ", "test tube and test"),
        
        # [9] Test cases for aligning tense (irregular verbs)
        ("enGiNe was broken", "engine is broken"),
        ("many leak were Formed", "many leak are formed"), # ! formed -> form ?
        ("metal pipe was broken", "metal pipe is broken"),
        ("gw had innadequate", "gland water has inadequate"),
        
        # [9] Test cases for aligning tense (regular verbs)
        # ("cpu running", "central processing unit running"), # ! running -> run ?
        # ("worked played busted", "work play bust"), # ! no code for aligning regular verbs 
        
        # [10] Test cases for pluralising
        ("glass", "glass"),  # double s endings
        ("slurries", "slurry"),  # ies > ry
        ("boxes", "box"),  # xes -> x
        ("pumps busted", "pump busted"), # ! busted -> bust ?
        # ("the glasses holds foxes and has holes", "the glasse hold fox and has hole") # ! glases -> glass ?
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
