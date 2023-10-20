import re
from typing import List
import pandas as pd

from .logger import logger


def normalise_dataframe(
    df: pd.DataFrame,
    text_column: str,
    corrections_dict: dict,
    max_words: int = None,
    drop_duplicates: bool = False,
) -> pd.DataFrame:
    """Summary

    Args:
        df (pd.DataFrame): The dataframe to normalise.
        text_column (str): The column containing the text to normalise.
        corrections_dict (dict): The dictionary of corrections.
        max_words (int, optional): If present, drop all rows where
           the text field contains > max_words words.
        drop_duplicates (bool, optional): If present, any rows where the
           specified column is a duplicate will be dropped.
    """

    # If drop_duplicates is True, drop rows accordingly
    if drop_duplicates:
        rows_before = len(df)
        df = df.drop_duplicates(subset=text_column, keep="first")
        rows_after = len(df)
        logger.info(
            f"Dropped {rows_before - rows_after} duplicate rows "
            f"({rows_before} -> {rows_after})."
        )

    # If max_words is present, drop all rows with > max_words
    if max_words:
        rows_before = len(df)
        df = df[df[text_column].apply(lambda x: len(x.split()) < max_words)]
        rows_after = len(df)
        logger.info(
            f"Dropped {rows_before - rows_after} rows with > {max_words} "
            f"words ({rows_before} -> {rows_after})."
        )

    # Run the normalisation over each row, on the text column
    df[text_column] = df[text_column].apply(
        lambda x: normalise_text(x, corrections_dict)
    )
    return df


def normalise_text(text: str, corrections_dict: dict) -> str:
    """Normalise the given text using a pipeline-based approach.

    Args:
        text (str): The text to normalise.

    Returns:
        str: The normalised text.
    """
    # 1. Lowercase text
    _text = text.lower()

    # 2. Add space around hypen
    _text = _add_space_around_hyphen(_text)

    # 3. Remove commas
    _text = _remove_commas(_text)

    # 4. Fix typos
    _text = _correct_typos(
        text=_text, corrections_dict=corrections_dict
    )  # i.e. "filters - filters accumulated due to contamination."

    # 5. Anonymise sentence
    _text = _anonymise_sentence(_text)
    # need help to loop through every sentence in the "NOTIFICATION_SHORT_TEXT" field

    # 6. Tokenize
    _tokens = _text.split(" ")  # i.e. ["filters", "-", ...]

    # 7. Pluralise - Function expects TOKENS not a STRING
    _tokens = [
        _singularise(token) for token in _tokens
    ]  # i.e. ["filter", "-", ...]

    # 8. Add space around slash
    _text = _space_around_slash(_text)

    # 9. Align tense - Function expects TOKENS not a STRING
    _tokens = [
        _to_present_tense(token) for token in _tokens
    ]  # i.e. [... "accumulat", ...]

    # 10. Recreate _text as string based on processed tokens.
    _text = " ".join(_tokens)

    return _text

    # QuickGraph fields `original`, `tokens`, `external_id`, `extra_fields`

    # _id = f'FLOC: {obj["Functional Location"]} RID: {obj["Risk ID"]}'

    # quickgraph_samples.append(
    #     {"original": _text, "tokens": _tokens, "external_id": _id}
    # )


def _singularise(word: str):
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


def _to_present_tense(verb: str) -> str:
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


def _correct_typos(text: str, corrections_dict: dict) -> str:
    """
    Corrects typos in a given string based on a mapping dictionary.

    Parameters:
    - text (str): The string containing potential typos.
    - corrections_dict (dict): A dictionary mapping incorrect words to their correct versions.

    Returns:
    - str: The corrected string.

    Examples:
    >>> replacement_dict = {'craked': 'cracked'}
    >>> correct_typos("The wall was craked.", replacement_dict)
    "The wall was cracked."
    """

    words = text.split()
    corrected_words = [corrections_dict.get(word, word) for word in words]
    return " ".join(corrected_words)


# First, we need to import the 're' module which provides support
# for regular expressions in Python.


def _anonymise_sentence(sentence):
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


def _remove_extra_spaces(text: str):
    # The pattern \s+ matches one or more whitespace characters.
    # It's then replaced with a single space.
    return re.sub(r"\s+", " ", text)


def _add_space_around_hyphen(text: str):
    # The pattern searches for a non-space character before and after a hyphen.
    # The replaced text will ensure spaces exist around the hyphen.
    return re.sub(r"(?<=[^\s])-|-(?=[^\s])", " - ", text)


def _space_around_slash(text: str):
    """This function will replace every "/" in the string with " / ",
    ensuring there's a space before and after each slash.

    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    return text.replace("/", " / ")


def _remove_commas(text):
    """Remove commas from the text.

    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    return text.replace(",", " ")
