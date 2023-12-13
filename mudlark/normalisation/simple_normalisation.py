"""Functions for normalising text."""
import re
from nltk import word_tokenize
from mudlark.utils import load_corrections_dict


def simple_normalise(text: str, corrections_path: str = None):
    """Run the 'simple' normalisation over the given text.

    Args:
        text (str): The text to normalise.
        corrections_path (str, optional): The path containing the
           corrections dictionary. If not present, will use the default.

    Returns:
        str: The normalised text.

    """

    corrections_dict = load_corrections_dict(corrections_path)
    
    # 1. Fix typos
    text = _correct_typos(
        text=text, corrections_dict=corrections_dict
    )  # i.e. "filters - filters accumulated due to contamination."

    # 2. Lowercase text
    text = text.lower()

    # 3. Add space around hypen
    text = _add_space_around_hyphen(text)

    # 4. Remove commas
    text = _remove_commas(text)

    # 5. Add space around slash
    text = _space_around_slash(text)

    # 6. Anonymise sentence
    text = _anonymise_sentence(text)

    # 7. Remove extra spaces
    text = _remove_extra_spaces(text)

    # 8. Tokenize
    tokens = word_tokenize(text)  # i.e. ["filters", "-", ...]

    # 9. Align tense - Function expects TOKENS not a STRING
    tokens = [
        _to_present_tense(verb=token, corrections_dict=corrections_dict) for token in tokens
    ]  # i.e. [... "accumulat", ...]

    # 10. Pluralise - Function expects TOKENS not a STRING
    tokens = [
        _singularise(token) for token in tokens
    ]  # i.e. ["filter", "-", ...]

    # 11. Recreate _text as string based on processed tokens.
    text = " ".join(tokens)

    return text


def _remove_extra_spaces(text):
    """Remove any superfluous spaces in the given text.

    Args:
        text (str): The text to remove the spaces from.

    Returns:
        str: The updated text.
    """
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
    if len(word) <= 3:  # Don't singularise short words (was, is, etc)
        return word
    if word.endswith("ss"):  # e.g., "glass" -> "glass"
        return word
    if word.endswith("ies") and len(word) > 3:  # e.g., "berries" -> "berry"
        return word[:-3] + "y"
    if word.endswith("xes") and len(word) > 2:  # e.g., "boxes" -> "box"
        return word[:-2]
    if word.endswith("ses") and len(word) > 3:  # e.g., "glasses" -> "glass"
        return word[:-2]
    if word.endswith("s") and len(word) > 1:  # e.g., "cats" -> "cat"
        return word[:-1]
    return word


def _to_present_tense(verb: str, corrections_dict: dict) -> str:
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
        "have": "has",
        "did": "do",
        "went": "go",
        "ran": "run",
    }
    if verb in irregulars:
        return irregulars[verb]
    
    # Ignore keywords from corrections_dict
    keywords_set = set()
    for terms in corrections_dict.values():
        words = str(terms).split()
        keywords_set.update(words)
    keywords = list(keywords_set)
    
    if verb not in keywords:
        endings = ["ing", "ed"]
        for ending in endings:
            if verb.endswith(ending):
                stem = verb[:-len(ending)]
                if len(stem) > 1:
                    if stem.endswith(("c", "k")) and not stem.endswith(("ck", "rk")):
                        return stem + "e"
                    if stem.endswith("nn") and ending == "ing":
                        return stem[:-1]
                return stem

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

    corrected_text = text
    for incorrect, corrected in corrections_dict.items():
        incorrect, corrected = str(incorrect), str(corrected)
        index = corrected_text.find(incorrect)
        
        if index != -1:
            if len(incorrect) < len(corrected):
                if corrected_text[index:index+len(corrected)] == corrected:
                    continue 
            corrected_text = corrected_text.replace(incorrect, corrected)
        
    return corrected_text


def _anonymise_sentence(sentence):
    """Anonymise the given sentence.

    The pattern to match asset identifiers is defined as follows:

    b: This represents a word boundary. It ensures that the pattern
    we're trying to match is treated as a distinct word, not as part
    of another word.

    [A-Za-z]*: This matches zero or more alphabetical characters. It covers
    patterns where an asset identifier might start with letters like "AB" in
    "AB12".

    d+: This matches one or more numeric characters. It ensures we match
    patterns that have numbers in them like "12" in "AB12".

    [A-Za-z]*: This again matches zero or more alphabetical characters.
    It covers patterns where an asset identifier might end with
    letters like "a" in "AB12a".

    b: Another word boundary to ensure the end of our matched pattern is
    also treated as a distinct word.

    Args:
        sentence (str): The sentence to anonymise.

    Returns:
        str: The anonymised sentence.
    """
    pattern = (
        r"\b(\d*[A-Za-z]+\d+[A-Za-z]*|[A-Za-z]*\d+[A-Za-z]+|"
        r"[A-Za-z]*\d+[A-Za-z]*|[A-Za-z]\d[A-Za-z]\d\d[A-Za-z])\b"
    )

    # Using the re.sub() method, we replace any substring in the 'sentence'
    # that matches our 'pattern' with the word "AssetID". This function
    # returns a new string where all the replacements have been made.
    anonymised_sentence = re.sub(pattern, "AssetID", sentence)

    # The modified sentence is then returned.
    return anonymised_sentence


def _add_space_around_hyphen(text: str):
    """Add space characters around a hyphen character.

    Args:
        text (str): The text to modify.

    Returns:
        str: The updated text.
    """
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
