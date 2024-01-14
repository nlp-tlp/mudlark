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
    if word.endswith("ies"):  # e.g., "berries" -> "berry"
        return word[:-3] + "y"
    if word.endswith("es") and ((word[-3] in ["o", "s", "x", "z"]) or (word[-4:-2] in ["sh", "ch"])):  # e.g., "glasses" -> "glass"
        return word[:-2]
    if word.endswith("s") and (word[-2] not in ["u"]):  # e.g., "cats" -> "cat"
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
        if verb.endswith("ed"):
            stem = verb[:-len("ed")]
            if len(stem) > 1:
                if stem.endswith(("c", "k")) and not stem.endswith(("ck", "rk")):
                    return stem + "e"
                else: return verb[:-2]

        elif (verb.endswith("ing")):
            # not verbs 
            ing_not_verbs = ["ceiling", "beesting", "beeswing", "hamstring", "lightning", "shilling", "willing", "unwilling","swing"]
            if verb in ing_not_verbs:
                return verb
            if re.findall(r"^[b-df-hj-np-tv-xz]+ing$",verb): # one syllable -ing words, e.g. "bring" -> "bring"
                return verb
            # dealing with one syllable root words
            if re.findall(r"^[b-df-hj-np-tv-z]+[aeiou]lling$",verb): # one syllable -lling words, e.g. "filling" -> "fill"
                return verb[:-3]
            if re.findall(r"^[b-df-hj-np-tv-z]ying$",verb):# two syllable -ying words, e.g. "tying" -> "tie"
                return verb[0] + "ie"
            if re.findall(r"^[aeiou][b-df-hj-np-tv-z]ing$",verb): # e.g., "using" -> "use"
                return verb[:-3] + "e" 
            
            # dealing with patterns
            double_letter_ending_verbs = r"^(ebbing|adding|superadding|odding|redding|egging|inning|erring|shirring|burring|deburring|flurring|skirring|purring|putting|vaxxing)$"
            multisyllable_ll_verbs = r"^(bankrolling|bespelling|bookselling|bushfelling|doomscrolling|enrolling|farewelling|hairpulling|handselling|inscrolling|kvelling|logrolling|misspelling|outpolling|outpulling|outrolling|outselling|outswelling|outwelling|outyelling|overselling|outsmelling|overswelling|preselling|reenrolling|repolling|rerolling|reselling|respelling|steamrolling|unrolling|underselling|uprolling|upselling|upswelling|upwelling)$"
            if re.findall(multisyllable_ll_verbs, verb):
                return verb[:-3]
            if re.findall(r"([bct]alling$)|(thralling$)", verb) and not re.findall(r"^(caballing|gimballing|metalling|pedastalling|totalling)$", verb):
                return verb[:-3]
            if verb == "chandelling" or verb == "cordelling":
                return verb[:-3] + "e" 
            if verb.endswith("telling"):
                return verb[:-3]
            illing_exceptions = r"^(imperilling|perilling|postilling)$"
            if re.findall(r"[bdf-hj-np-tw-z]illing$",verb) and not re.findall(illing_exceptions, verb):
                return verb[:-3]
            if re.findall(r"([b-dghj-np-rtv])\1ing$",verb) and not re.findall(double_letter_ending_verbs, verb): # e.g., "jogging" -> "jog"
                return verb[:-4]
            if re.findall(r"[b-df-hj-np-tv-z][aeiou][b-df-hj-npqstvz]ing$",verb): # e.g., "hoping" -> "hope"
                return verb[:-3] + "e" 
            
            # two vowel syllable division exceptions
            syllable_division_exceptions = ["enucleating","ideating","malleating","nucleating","permeating","illaqueating","laureating","nauseating"]
            if verb in syllable_division_exceptions:
                return verb[:-3] + "e"
            # ea
            if verb.endswith("creating"): # e.g. "recreating" -> "recreate"
                return verb[:-3] + "e"
            if verb.endswith("lineating"): # e.g. "lineating" -> "lineate"
                return verb[:-3] + "e"
            if verb.endswith("caseating"): # e.g. "caseating" -> "caseate"
                return verb[:-3] + "e"
            # ia
            if verb.endswith("aliasing"): # e.g. "aliasing" -> "alias"
                return verb[:-3]
            if verb.endswith("biasing"): # e.g. "biasing" -> "bias"
                return verb[:-3]
            if re.findall(r"ia[b-df-hjkmnp-tv-z]ing$",verb): # removing special case -ialing
                return verb[:-3] + "e"
            
            
            # vowel digraphs
            # au_ing
            if verb.endswith("auging"): # deals with "au" exceptions, e.g. "gauging" -> "gauge" 
                return verb[:-3] + "e" 
            # ea_ing 
            ea_inclusions = ["bequeathing", "freathing"]
            if verb in ea_inclusions:
                return verb[:-3]
            if verb.endswith("eathing"): # deals with "ea" exceptions, e.g. "breathing" -> "breathe" 
                return verb[:-3] + "e"
            # ee_ing
            ee_exclusions = ["teething", "seething"]
            if verb in ee_exclusions:
                return verb[:-3] + "e"
            # eu_ing 
            if verb.endswith("euning"): # e.g. "reuning" -> "reune"
                return verb[:-3] + "e"
            # ie_ing
            ie_exclusions = ["julienning"]
            if verb in ie_exclusions:
                return verb[:-3] + "e"
            # oo_ing 
            oo_exceptions = ["soogeing"]
            if verb in oo_exceptions:
                return verb[:-3] + "e"
            # ou_ing
            ou_exceptions = ["routing","misrouting","rerouting","douching","accouching"]
            if verb in ou_exceptions:
                return verb[:-3] + "e"
            if verb.endswith("ouging"): # e.g. "scrouging" -> "scrouge"
                return verb[:-3] + "e"
            # ua_ing
            if re.findall(r"ua[dgktr]ing$",verb): # deals with "ua" exceptions, e.g. "arranging" -> "arrange" 
                return verb[:-3] + "e" 
            # ue_ing
            if verb == "queuing":
                return verb[:-3] + "e" 
            # ui_ing
            if re.findall(r"ui[rdl]ing$",verb): # deals with "ui" exceptions, e.g. "arranging" -> "arrange" 
                return verb[:-3] + "e" 
            if verb == "requiting":
                return verb[:-3] + "e" 
            
            
            # going down alphabetically and dealing with exceptions 
            # c
            if verb.endswith("cing"): # deals with -cing, e.g. "bouncing" -> "bounce"
                return verb[:-3] + "e" 
            # f 
            ff_exceptions = r"^(coiffing|piaffing)$"
            if re.findall(ff_exceptions,verb): # deals with -ffing, e.g. "coiffing" -> "coiffe"
                return verb[:-3] + "e" 
            # g 
            if re.findall(r"[rdl]ging$",verb): # deals with -rging, -dging, -lging, e.g. "dodging" -> "dodge"
                return verb[:-3] + "e" 
            if verb.endswith("changing"): 
                return verb[:-3] + "e" 
            ranging_inclusions = r"^(boomeranging|pranging)$"
            if verb.endswith("ranging") and not re.findall(ranging_inclusions,verb): 
                return verb[:-3] + "e" 
            if verb.endswith("enging"):
                return verb[:-3] + "e" 
            inging_inclusions = r"^(pinging|bringing|outringing|outspringing|overstringing|ringing|springing|stringing|understringing|unstringing|upbringing|upspringing|wringing|attinging)$"
            if re.findall(r"[bcf-hjkmp-rtv]inging$",verb) and not re.findall(inging_inclusions,verb):
                return verb[:-3] + "e" 
            unging_inclusions = r"^(dunging|bunging)$"
            if verb.endswith("unging") and not re.findall(unging_inclusions, verb):
                return verb[:-3] + "e" 
            ng_exceptions = r"^(flanging|twinging|sponging)$"
            if re.findall(ng_exceptions, verb):
                return verb[:-3] + "e" 
            # l
            if re.findall(r"[b-df-hj-np-tvz]ling$",verb): # deals with <consonant sound> + ling, e.g. "trembling" -> "tremble"
                return verb[:-3] + "e" 
            # r
            if re.findall(r"[b-df-hj-np-tv-z]+[aiu]ring$",verb): # deals with <consonant sound> + ling, e.g. "trembling" -> "tremble"
                return verb[:-3] + "e" 
            inclusions_ering = ["adhering", "interfering", "premiering", "revering"]
            if verb in inclusions_ering: # deals with <consonant sound> + ling, e.g. "trembling" -> "tremble"
                return verb[:-3] + "e" 
            exceptions_oring = r"(coloring|tailoring|sailoring|authoring|anchoring|vaporing)$"
            incusions_oring = r"^(snoring|storing|restoring|boring|chokeboring|reboring|counterboring)$"
            if re.findall(incusions_oring + r"|^[b-df-hj-np-tv-z]+oring$",verb) or ( re.findall(r"[ldhp]oring$",verb) and not re.findall(exceptions_oring,verb) ): # deals with -oring that should add an e, e.g. "requiring" -> "require"
                return verb[:-3] + "e" 
            if re.findall(r"uiring$",verb): # deals with -uiring, e.g. "requiring" -> "require"
                return verb[:-3] + "e" 
            # s
            if verb.endswith("ssing"): # deals with -ssing, e.g. "accessing" -> "access"
                return verb[:-3]
            if verb.endswith("sing"): # deals with -sing, e.g. "housing" -> "house"
                return verb[:-3] + "e" 
            # u
            if verb.endswith("uing"): # e.g. "subduing" -> "subdue"
                return verb[:-3] + "e" 
            # v 
            if verb.endswith("ving"): # e.g. "solving" -> "solve"
                return verb[:-3] + "e" 
            # z
            z_exceptions = r"^(whizzing|quizzing)$"
            if re.findall(z_exceptions,verb): # deals with -uiring, e.g. "requiring" -> "require"
                return verb[:-4]
            if verb.endswith("zzing"): # e.g. "buzzing" -> "buzz"
                return verb[:-3]
            if verb.endswith("zing"): # e.g. "buzzing" -> "buzz"
                return verb[:-3] + "e"
            
            
            
            return verb[:-3]


    # if verb not in keywords:
    #     endings = ["ing", "ed"]
    #     for ending in endings:
    #         if verb.endswith(ending):
    #             stem = verb[:-len(ending)]
    #             if len(stem) > 1:
    #                 if stem.endswith(("c", "k")) and not stem.endswith(("ck", "rk")):
    #                     return stem + "e"
    #                 if stem.endswith("nn") and ending == "ing":
    #                     return stem[:-1]
    #             return stem

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
        replace = r"\b"+incorrect+r"\b"
        corrected_text = re.sub(replace, corrected, corrected_text)
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
