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

    stem = ""
    if verb not in keywords:
        if verb.endswith("ed"):
            stem = verb[:-len("ed")]
            # if len(stem) > 1:
            #     if stem.endswith(("c", "k")) and not stem.endswith(("ck", "rk")):
            #         return stem + "e"
            #     else: return verb[:-2]
            if len(stem) <= 1:
                return verb

        elif (verb.endswith("ing")):
            stem = verb[:-len("ing")]
            # not verbs 
            ing_not_verbs = r"^(ceiling|building|beesting|beeswing|hamstring|lightning|shilling|willing|unwilling|upbringing)$"
            if re.findall(ing_not_verbs, verb):
                return verb
            
        else: 
            return verb
        
        if re.findall(r"^[b-df-hj-np-tv-xz]+$",stem): # one syllable -ing words, e.g. "bring" -> "bring"
            return verb
        
        # dealing with one syllable root words
        if re.findall(r"^[b-df-hj-np-tv-z]+[aeiou]ll$",stem): # one syllable -lling words, e.g. "filling" -> "fill"
            return stem
        if re.findall(r"^[b-df-hj-np-tv-z]ying$",verb): # two syllable -ying words, e.g. "tying" -> "tie"
            return verb[0] + "ie"
        if re.findall(r"^[b-df-hj-np-tv-z]yed$",verb): # one syllable -yed exceptions, e.g "dyed" -> "dye"
            return verb[:-1]
        if re.findall(r"^[b-df-hj-np-tv-z]ied$",verb):
            return verb[0] + "ie"
        if re.findall(r"^[aeiou][b-df-hj-np-tv-z]$",stem): # e.g. "using" -> "use"
            return stem + "e" 
        
        # dealing with patterns
        double_letter_ending_verbs = r"^(ebb|add|superadd|odd|redd|egg|inn|err|shirr|\
            burr|deburr|flurr|skirr|purr|putt|vaxx)$"
        multisyllable_ll_verbs = r"^(bankroll|bespell|booksell|bushfell|doomscroll|enroll|\
            farewell|hairpull|handsell|inscroll|kvell|logroll|misspell|outpoll|outpull|\
                outroll|outsell|outswell|outwell|outyell|oversell|outsmell|overswell|\
                    presell|reenroll|repoll|reroll|resell|respell|steamroll|unroll|\
                        undersell|uproll|upsell|upswell|upwell)$"
        if re.findall(multisyllable_ll_verbs, stem):
            return stem
        if re.findall(r"([bct]all$)|(thrall$)", stem) and not re.findall(r"^(caball|gimball|metall|pedastall|totall)$", stem):
            return stem
        if re.findall(r"^(chandell|cordell)$", stem):
            return stem + "e" 
        if stem.endswith("tell"):
            return stem
        illing_exceptions = r"^(imperill|perill|postill)$"
        if re.findall(r"[bdf-hj-np-tw-z]ill$", stem) and not re.findall(illing_exceptions, stem):
            return stem
        if re.findall(r"([b-dghj-np-rtv])\1$",stem) and not re.findall(double_letter_ending_verbs, stem): # e.g., "jogging" -> "jog"
            return stem[:-1]
        if re.findall(r"[b-df-hj-np-tv-z][aeiou][b-df-hj-npqstvz]$",stem): # e.g., "hoping" -> "hope"
            return stem + "e" 
        
        # two vowel syllable division exceptions
        syllable_division_exceptions = r"^(enucleat|ideat|malleat|nucleat|permeat|illaqueat|laureat|nauseat)$"
        if re.findall(syllable_division_exceptions, stem):
            return stem + "e"
        # ea
        if stem.endswith("creat"): # e.g. "recreating" -> "recreate"
            return stem + "e"
        if stem.endswith("lineat"): # e.g. "lineating" -> "lineate"
            return stem + "e"
        if stem.endswith("caseat"): # e.g. "caseating" -> "caseate"
            return stem + "e"
        # ia
        if stem.endswith("alias"): # e.g. "aliasing" -> "alias"
            return stem
        if stem.endswith("bias"): # e.g. "biasing" -> "bias"
            return stem
        if re.findall(r"ia[b-df-hjkmnp-tv-z]$",stem): # removing special case -ialing
            return stem + "e"
        
        
        # vowel digraphs
        # au_ing
        if stem.endswith("aug"): # deals with "au" exceptions, e.g. "gauging" -> "gauge" 
            return stem + "e" 
        # ea_ing 
        ea_inclusions = r"^(bequeath|freath)$"
        if re.findall(ea_inclusions, stem):
            return stem
        if stem.endswith("eath"): # deals with "ea" exceptions, e.g. "breathing" -> "breathe" 
            return stem + "e"
        # ee_ing
        ee_exclusions = r"^(teeth|seeth)$"
        if re.findall(ee_exclusions, stem):
            return stem + "e"
        ee_ed_form = r"^(agreed|decreed|demareed|disagreed|emceed|farseed|filigreed|freed|fricasseed|\
            garnisheed|gratineed|guaranteed|kneed|leveed|peed|pureed|shivareed|squeegeed|squeed|teed|treed|trusteed)$"
        if re.findall(ee_ed_form, verb):
            return verb[:-1]
        if verb.endswith("eed"):
            return verb
        # eu_ing 
        if stem.endswith("eun"): # e.g. "reuning" -> "reune"
            return stem + "e"
        # ie_ing
        ie_exclusions = r"^julienn$"
        if re.findall(ie_exclusions, stem):
            return stem + "e"
        # oo_ing 
        oo_exceptions = r"^sooge$"
        if re.findall(oo_exceptions, stem):
            return stem + "e"
        # ou_ing
        ou_exceptions = r"^(rout|misrout|rerout|douch|accouch)$"
        if re.findall(ou_exceptions, stem):
            return stem + "e"
        if stem.endswith("oug"): # e.g. "scrouging" -> "scrouge"
            return stem + "e"
        # ua_ing
        if re.findall(r"ua[dgktr]$", stem): # deals with "ua" exceptions, e.g. "arranging" -> "arrange" 
            return stem + "e" 
        # ue_ing
        if stem == "queu":
            return stem + "e" 
        # ui_ing
        if re.findall(r"ui[rdl]$", stem): # deals with "ui" exceptions, e.g. "arranging" -> "arrange" 
            return stem + "e" 
        if stem == "requit":
            return stem + "e" 
        
        
        # going down alphabetically and dealing with exceptions 
        # c
        if stem.endswith("c"): # deals with -cing, e.g. "bouncing" -> "bounce"
            return stem + "e" 
        # f 
        ff_exceptions = r"^(coiff|piaff)$"
        if re.findall(ff_exceptions,stem): # deals with -ffing, e.g. "coiffing" -> "coiffe"
            return stem + "e" 
        # g 
        if re.findall(r"[rdl]g$",stem): # deals with -rging, -dging, -lging, e.g. "dodging" -> "dodge"
            return stem + "e" 
        if stem.endswith("chang"): 
            return stem + "e" 
        ranging_inclusions = r"^(boomerang|prang)$"
        if stem.endswith("rang") and not re.findall(ranging_inclusions,stem): 
            return stem + "e" 
        if stem.endswith("eng"):
            return stem + "e" 
        inging_ing_specific_inclusions = r"^(bringing|outringing|outspringing|understringing|unstringing|upspringing)$"
        inging_inclusions = r"^(ping|overstring|ring|spring|string|wring)$"
        if re.findall(r"[bcf-hjkmp-rtv]ing$",stem) and not re.findall(inging_ing_specific_inclusions,verb) and not re.findall(inging_inclusions,stem):
            return stem + "e" 
        unging_inclusions = r"^(dung|bung)$"
        if stem.endswith("ung") and not re.findall(unging_inclusions, stem):
            return stem + "e" 
        ng_exceptions = r"^(flang|twing|spong)$"
        if re.findall(ng_exceptions, stem):
            return stem + "e" 
        # i 
        if verb.endswith("ied"):
            return stem[:-1]+"y"
        # l
        if re.findall(r"[b-df-hj-np-tvz]l$",stem): # deals with <consonant sound> + ling, e.g. "trembling" -> "tremble"
            return stem + "e" 
        # r
        if re.findall(r"[b-df-hj-np-tv-z]+[aiu]r$",stem): # deals with <consonant sound> + ling, e.g. "trembling" -> "tremble"
            return stem + "e" 
        ering_exclusions = r"^(adher|interfer|premier|rever)$"
        if stem in ering_exclusions: # deals with <consonant sound> + ling, e.g. "trembling" -> "tremble"
            return stem + "e" 
        oring_incusions = r"(color|tailor|sailor|author|anchor|vapor)$"
        oring_exceptions = r"^(snor|stor|restor|bor|chokebor|rebor|counterbor)$"
        if re.findall(oring_exceptions + r"|^[b-df-hj-np-tv-z]+or$",stem) or ( re.findall(r"[ldhp]or$",stem) and not re.findall(oring_incusions,stem) ): # deals with -oring that should add an e, e.g. "storing" -> "store"
            return stem + "e" 
        if re.findall(r"uir$",stem): # deals with -uiring, e.g. "requiring" -> "require"
            return stem + "e" 
        # s
        if stem.endswith("ss"): # deals with -ssing, e.g. "accessing" -> "access"
            return stem
        if stem.endswith("s"): # deals with -sing, e.g. "housing" -> "house"
            return stem + "e" 
        # u
        if stem.endswith("u"): # e.g. "subduing" -> "subdue"
            return stem + "e" 
        # v 
        if stem.endswith("v"): # e.g. "solving" -> "solve"
            return stem + "e" 
        # z
        z_exceptions = r"^(whizz|quizz)$"
        if re.findall(z_exceptions,stem): # deals with -uiring, e.g. "requiring" -> "require"
            return stem[:-1]
        if stem.endswith("zz"): # e.g. "buzzing" -> "buzz"
            return stem
        if stem.endswith("z"): # e.g. "buzzing" -> "buzz"
            return stem + "e"
            
            
            
        return stem


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
