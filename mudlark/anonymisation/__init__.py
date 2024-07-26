import re


def get_anonymised_terms(sentence):
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
    # pattern = re.compile(
    #     r"\b(\d*[A-Za-z]+\d+[A-Za-z]*|[A-Za-z]*\d+[A-Za-z]+|"
    #     r"[A-Za-z]*\d+[A-Za-z]*|[A-Za-z]\d[A-Za-z]\d\d[A-Za-z])\b"
    # )
    #

    # Pattern one (ABC-123, ABC 123, ABC123 etc)
    pattern_1 = re.compile(r"\b[A-Z]+\s*-*\d+\b")
    # pattern_2 = re.compile(r"\b\d+\s*-*[A-Z]+\b")
    anonymised_terms = set()

    # Ignore measurement related items
    # unwanted_pattern = re.compile(
    #    r"\d+(deg|a|kv|v|w|wk|amp|l|kl|ml|w|mm|m|km|hr|hrs|x|g|kg|t|d|y|yr)s?"
    # )

    # Using the re.sub() method, we replace any substring in the 'sentence'
    # that matches our 'pattern' with the word "asset_id". This function
    # returns a new string where all the replacements have been made.
    matches_1 = re.findall(pattern_1, sentence)
    # matches_2 = re.findall(pattern_2, sentence)
    matches = matches_1
    for m in matches:
        # if m.startswith("Asset") or len(m) <= 1 or m.isnumeric():
        #    continue
        # if re.match(unwanted_pattern, m):
        #    continue
        # sentence = sentence.replace(m, "AssetID")
        anonymised_terms.add(m)

    # The modified sentence is then returned.
    return anonymised_terms
