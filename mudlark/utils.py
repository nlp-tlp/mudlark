import configparser
import pandas as pd
from typing import List


def singularise(word: str):
    """
    Attempts to convert a plural word to its singular form.

    This function handles common plural endings such as "s", "es", and "ies".
    Note that it won't handle irregular plurals or all complexities of the English language.


    Returns:
    - str: The singular form of the given word.

    Examples:
    >>> singularize("berries")
    "berry"
    >>> singularize("boxes")
    "box"
    >>> singularize("cats")
    "cat"

    Args:
        word (str): The word to singularise.

    Returns:
        str: The singular form of the given word.
    """
    if word.endswith("ss"):  # e.g., "glass" -> "glass"
        return word
    elif word.endswith("ies") and len(word) > 3:  # e.g., "berries" -> "berry"
        return word[:-3] + "y"
    elif word.endswith("xes") and len(word) > 2:  # e.g., "boxes" -> "box"
        return word[:-2]
    elif word.endswith("s") and len(word) > 1:  # e.g., "cats" -> "cat"
        return word[:-1]
    else:
        return word


def to_present_tense(verb: str) -> str:
    """
    Attempts to convert a verb to its present tense.

    This function handles common verb endings but won't handle all irregular verbs or complexities of the English language.

    Parameters:
    - verb (str): The verb to be converted to present tense.

    Returns:
    - str: The present tense form of the given verb.

    Examples:
    >>> to_present_tense("played")
    "play"
    >>> to_present_tense("running")
    "run"
    """

    # Handling some irregular verbs
    irregulars = {
        "was": "is",
        "were": "are",
        "had": "has",
        "did": "do",
        "went": "go",
    }
    if verb in irregulars:
        return irregulars[verb]

    # Handling common verb endings
    if verb.endswith("ormed"):
        return verb
    elif verb.endswith("med"):
        return verb[:-3]
    else:
        return verb


def correct_typos(text: str, replacement_dict: dict) -> str:
    """
    Corrects typos in a given string based on a mapping dictionary.

    Parameters:
    - text (str): The string containing potential typos.
    - replacement_dict (dict): A dictionary mapping incorrect words to their correct versions.

    Returns:
    - str: The corrected string.

    Examples:
    >>> replacement_dict = {'craked': 'cracked'}
    >>> correct_typos("The wall was craked.", replacement_dict)
    "The wall was cracked."
    """

    words = text.split()
    corrected_words = [replacement_dict.get(word, word) for word in words]
    return " ".join(corrected_words)


# First, we need to import the 're' module which provides support
# for regular expressions in Python.


def anonymise_sentence(sentence):
    # The pattern to match asset identifiers is defined as follows:
    #
    # \b: This represents a word boundary. It ensures that the pattern we're trying
    #     to match is treated as a distinct word, not as part of another word.
    #
    # [A-Za-z]*: This matches zero or more alphabetical characters. It covers
    #           patterns where an asset identifier might start with letters like "AB" in "AB12".
    #
    # \d+: This matches one or more numeric characters. It ensures we match
    #      patterns that have numbers in them like "12" in "AB12".
    #
    # [A-Za-z]*: This again matches zero or more alphabetical characters.
    #           It covers patterns where an asset identifier might end with letters like "a" in "AB12a".
    #
    # \b: Another word boundary to ensure the end of our matched pattern is also treated as a distinct word.
    pattern = r"\b(\d*[A-Za-z]+\d+[A-Za-z]*|[A-Za-z]*\d+[A-Za-z]+|[A-Za-z]*\d+[A-Za-z]*|[A-Za-z]\d[A-Za-z]\d\d[A-Za-z])\b"

    # Using the re.sub() method, we replace any substring in the 'sentence' that
    # matches our 'pattern' with the word "AssetID". This function returns a new
    # string where all the replacements have been made.
    anonymised_sentence = re.sub(pattern, "AssetID", sentence)

    # The modified sentence is then returned.
    return anonymised_sentence


# To test the function, we provide a sample sentence and call the function.
# sentence = 'PU1760 not pumping'
# print(anonymise_sentence(sentence))  # This should output: 'AssetID not pumping'


def remove_extra_spaces(text: str):
    # The pattern \s+ matches one or more whitespace characters.
    # It's then replaced with a single space.
    return re.sub(r"\s+", " ", text)


def add_space_around_hyphen(text: str):
    # The pattern searches for a non-space character before and after a hyphen.
    # The replaced text will ensure spaces exist around the hyphen.
    return re.sub(r"(?<=[^\s])-|-(?=[^\s])", " - ", text)


def space_around_slash(text: str):
    """This function will replace every "/" in the string with " / ",
    ensuring there's a space before and after each slash.

    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    return text.replace("/", " / ")


def remove_commas(text):
    """Remove commas from the text.

    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    return text.replace(",", " ")


def load_csv_file(path: str):
    """Use Pandas to load the CSV file at the given path.

    Args:
        path (str): The file to load.

    Returns:
        pd.DataFrame: The pandas dataframe.
    """
    df = pd.read_csv(path)
    return df


def extract_keep_columns(kc: str) -> List[str]:
    """Extract the 'keep columns' from the user-specified string.
    It should be a list of columns the user wants to keep,
    separated by comma.

    Args:
        kc (str): The string to parse.

    Returns:
        list[str]: The list of columns.
    """
    return [s.strip() for s in kc.split(",")]


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)
    return {k: v for (k, v) in config.items("DEFAULT")}
