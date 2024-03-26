"""Tests for the normalise_text function."""
import pytest
from mudlark import normalise_text


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # [1] Test cases for lowercasing
        ("THERMOSTAT uNsErViceABLE", "thermostat unserviceable"),
        ("UpperCase", "uppercase"),
        ("MixedCaSe", "mixedcase"),
        ("Test Tube", "test tube"),

        # [2] Test cases for removing commas
        ("test,tube", "test tube"),
        ("engine,pump,pipe", "engine pump pipe"),
        ("broken,,,pump", "broken pump"),

        # [3] Test cases for removing undesirable characters
        ("leaking !%^ in ()pipes",  "leak in pipe"),

        # [4] Test cases for removing duplicate contiguous
        ("###engine broken@@@",  "# engine broken @"),

        # [5] Test cases for adding spaces around punctuations
        ("repair?!fix'.monitor",  "repair fix . monitor"),
        # Handle hyphens and slashes exceptions
        ("test-tube", "test - tube"),
        ("test/tube", "test / tube"),
        ("o-ring long-ring", "o-ring long - ring"),
        ("c/o replace/repair", "change out replace / repair"),
        ("HELLO/hi hey/HEY hi/hey HI/hi", "hello/hi hey / hey hi/hey hi/hi"),
        ("HELLO-hi hey-HEY hi-hey HI-hi", "hello-hi hey - hey hi-hey hi-hi"), 
        ("word-hyphen-word", "word - hyphen - word"),
        ("word/slash/word", "word / slash / word"),

        # [6] Test cases for anonymising text
        ("check ABX32ad and DDdkL204ddd", "check AssetID and AssetID"),
        ("AB123 XYZ789", "AssetID AssetID"),
        ("none here", "none here"),
        ("XY345Z", "AssetID"),

        # [7] Test cases for removing extra spaces
        ("replace   pump", "replace pump"),
        ("  test     tube   and   test  ", "test tube and test"),

        # [8] Test cases for fixing typos
        ("a/c leakin", "air conditioner leak"),
        ("accum boken", "accumulator broken"),
        ("conmon", "condition monitoring"),
        ("wtp reapair and repalce", "water treatment pump repair and replace"),
        ("gw innadequate", "gland water inadequate"),
        ("PLC", "programmable logic controller"),
        ("ROM", "run of mine"),
        ("BFWP", "boiler feed water pump"),
        ("air / con", "air conditioner"),
        ("air - con", "air conditioner"),
        ("two way", "two way radio"),
        ("hold", "hold"), # Test that it doesn't correct string within a word

        # [9] Test cases for aligning tense (irregular verbs)
        ("enGiNe was broken", "engine is broken"),
        ("many leak were Formed", "many leak are form"),
        ("metal pipe was broken", "metal pipe is broken"),
        ("gw had innadequate", "gland water has inadequate"),
        # [9] Test cases for aligning tense (regular verbs)
        ("batterie running", "battery run"),
        ("worked played busted jumped", "work play bust jump"),
        ("spinning stunning", "spin stun"), # double n
        ("liked baked danced lurked", "like bake dance lurk"),
        ("hiking crying bouncing licking", "hike cry bounce lick"),

        # [10] Test cases for singularising
        ("buses foxes bushes churches", "bus fox bush church"),  # es -> s
        ("oranges houses niches", "orange house niche"),  # es -> s
        ("berries slurries pies", "berry slurry pie"),  # ies -> y
        ("potatoes", "potato"),  # oes -> o
        ("indices vertices", "index vertex"),  # ces -> ex
        ("matrices appendices", "matrix appendix"),  # ces -> x
        ("elves dwarves leaves", "elf dwarf leaf"), # lves -> f, eves -> f
        ("knives wives", "knife wife"), # ives -> fe
        ("theses analyses", "thesis analysis"),  # es -> is
        ("data bacteria", "datum bacterium"),  # a -> um
        ("phenomena criteria", "phenomenon criterion"),  # a -> on
        ("radii foci fungi nuclei cacti", "radius focus fungus nucleus cactus"),  # i -> us
        ("rays boys", "ray boy"),  # ys -> y
        ("glass pass class", "glass pass class"),  # double s endings
        ("glasses classes dresses", "glass class dress"),  # sses -> ss
        ("pumps busted", "pump bust"), # pumps -> pump
        ("the foxes buys glasses", "the fox buy glass"),
        ("pens focus tennis campuses", "pen focus tennis campus"),  # general case
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
