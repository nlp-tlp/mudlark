import re
import json
from typing import List
import pandas as pd
from nltk import word_tokenize

from .logger import logger


def normalise_dataframe(
    df: pd.DataFrame,
    output_path: str,
    text_column: str,
    corrections_dict: dict,
    output_format: str,
    max_rows: int = None,
    max_words: int = None,
    drop_duplicates: bool = False,
    csv_keep_columns: list = None,
    quickgraph_id_columns: list = None,
) -> pd.DataFrame:
    """Normalise the given dataframe.

    Args:
        df (pd.DataFrame): The dataframe to normalise.
        output_path (str): The path to save the output to.
        text_column (str): The column containing the text to normalise.
        corrections_dict (dict): The dictionary of corrections.
        output_format (str): The output format. Can be either
           'csv' or 'quickgraph'.
        max_rows (int, optional): If present, randomly sample and truncate
           to max_rows.
        max_words (int, optional): If present, drop all rows where
           the text field contains > max_words words.
        drop_duplicates (bool, optional): If present, any rows where the
           specified column is a duplicate will be dropped.
        csv_keep_columns (list, optional): If present, only the given columns
           will be kept in the output.
        quickgraph_id_columns (list, optional): If present, the given columns
           will be used to form a composite id key to include in the output
           (only when the 'quickgraph' format is used).
    """

    # If keep_columns is present, drop all columns not in this list
    # (and always keep the text_column).
    if csv_keep_columns and output_format == "csv":
        df = _run_drop_unwanted_columns(df, csv_keep_columns, text_column)

    # If drop_duplicates is True, drop rows accordingly
    if drop_duplicates:
        df = _run_drop_duplicates(df, text_column)

    # If max_words is present, drop all rows with > max_words
    if max_words:
        df = _run_drop_long_rows(df, text_column, max_words)

    # Run the normalisation over each row, on the text column
    df[text_column] = df[text_column].apply(
        lambda x: normalise(x, corrections_dict)
    )

    # If max rows, randomly sample
    if max_rows:
        df = df.sample(n=max_rows)
        logger.info(f"Randomly sampled to {len(df)} rows.")

    return df


def normalise(text: str, corrections_dict: dict) -> str:
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

    # 6. Add space around slash
    _text = _space_around_slash(_text)

    # 7. Remove extra spaces
    _text = _remove_extra_spaces(_text)

    # 8. Tokenize
    _tokens = word_tokenize(_text)  # i.e. ["filters", "-", ...]

    # 9. Pluralise - Function expects TOKENS not a STRING
    _tokens = [
        _singularise(token) for token in _tokens
    ]  # i.e. ["filter", "-", ...]

    # 10. Align tense - Function expects TOKENS not a STRING
    _tokens = [
        _to_present_tense(token) for token in _tokens
    ]  # i.e. [... "accumulat", ...]

    # 11. Recreate _text as string based on processed tokens.
    _text = " ".join(_tokens)

    return _text


def _run_drop_unwanted_columns(
    df: pd.DataFrame, keep_columns: list, text_column: str
) -> pd.DataFrame:
    """Remove any columns in the given DataFrame that are not listed in
    keep_columns.

    Args:
        df (pd.DataFrame): DataFrame to modify.
        keep_columns (list): The list of columns that should be kept.
        text_column (str): The text column. This will always be kept.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    for c in keep_columns:
        if c not in df:
            raise ValueError(
                f"The column '{c}' was not found in the input dataset. "
                "Please check all columns listed in the 'keep_columns' list "
                "exist in the input dataset."
            )

    cols_before = len(df.columns)
    df = df[df.columns.intersection(keep_columns + [text_column])]
    cols_after = len(df.columns)
    logger.info(f"Dropped {cols_before - cols_after} unwanted columns.")

    return df


def _run_drop_duplicates(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """Remove duplicate rows.

    Args:
        df (pd.DataFrame): DataFrame to modify.
        text_column (str): The text column (duplicates of this column
           will be dropped).

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    rows_before = len(df)
    df = df.drop_duplicates(subset=text_column, keep="first")
    rows_after = len(df)
    logger.info(
        f"Dropped {rows_before - rows_after} duplicate rows "
        f"({rows_before} -> {rows_after})."
    )
    return df


def _run_drop_long_rows(
    df: pd.DataFrame, text_column: str, max_words: int
) -> pd.DataFrame:
    """Remove rows where the text column has > max_words.

    Args:
        df (pd.DataFrame): DataFrame to modify.
        text_column (str): The text column (duplicates of this column
           will be dropped).
        max_words (int): The max words allowed in the text column.

    No Longer Returned:
        pd.DataFrame: The modified DataFrame.
    """
    rows_before = len(df)
    df = df[df[text_column].apply(lambda x: len(x.split()) < max_words)]
    rows_after = len(df)
    logger.info(
        f"Dropped {rows_before - rows_after} rows with > {max_words} "
        f"words ({rows_before} -> {rows_after})."
    )
    return df


def _remove_extra_spaces(text):
    # The pattern \s+ matches one or more whitespace characters.
    # It's then replaced with a single space.
    return re.sub(r"\s+", " ", text)


def _singularise(word: str):
    """
    Attempts to convert a plural word to its singular form.

    This function handles common plural endings such as "s", "es", and "ies".
    Note that it won't handle irregular plurals or all complexities of the
    English language.


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

    This function handles common verb endings but won't handle all irregular
    verbs or complexities of the English language.

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
    - corrections_dict (dict): A dictionary mapping incorrect words to
    their correct versions.

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


def _anonymise_sentence(sentence):
    """Anonymise the given sentence.

    Args:
        sentence (str): The sentence to anonymise.

    Returns:
        str: The anonymised sentence.
    """
    # The pattern to match asset identifiers is defined as follows:
    #
    # \b: This represents a word boundary. It ensures that the pattern
    # we're trying
    #     to match is treated as a distinct word, not as part of another word.
    #
    # [A-Za-z]*: This matches zero or more alphabetical characters. It covers
    # patterns where an asset identifier might start with letters like "AB" in
    # "AB12".
    #
    # \d+: This matches one or more numeric characters. It ensures we match
    #      patterns that have numbers in them like "12" in "AB12".
    #
    # [A-Za-z]*: This again matches zero or more alphabetical characters.
    # It covers patterns where an asset identifier might end with
    # letters like "a" in "AB12a".
    #
    # \b: Another word boundary to ensure the end of our matched pattern is
    # also treated as a distinct word.
    pattern = r"\b(\d*[A-Za-z]+\d+[A-Za-z]*|[A-Za-z]*\d+[A-Za-z]+|[A-Za-z]*\d+[A-Za-z]*|[A-Za-z]\d[A-Za-z]\d\d[A-Za-z])\b"

    # Using the re.sub() method, we replace any substring in the 'sentence'
    # that matches our 'pattern' with the word "AssetID". This function
    # returns a new string where all the replacements have been made.
    anonymised_sentence = re.sub(pattern, "AssetID", sentence)

    # The modified sentence is then returned.
    return anonymised_sentence


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
