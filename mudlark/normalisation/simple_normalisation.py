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

    # 1. Lowercase text
    text = text.lower()

    # 2. Remove commas
    text = _remove_commas(text)

    # 3. Remove undesirable characters
    text = _remove_undesirable_chars(text)

    # 4. Remove duplicate contiguous characters
    text = _remove_duplicate_contiguous_chars(text)

    # 5. Add space around punctuation
    text = _add_space_around_punctuation(text)

    # 6. Anonymise sentence
    text = _anonymise_sentence(text)

    # 7. Remove extra spaces
    text = _remove_extra_spaces(text)

    # 8. Fix typos
    text = _correct_typos(
        text=text, corrections_dict=corrections_dict
    )  # i.e. "filters - filters accumulated due to contamination."

    # 9. Tokenize
    tokens = word_tokenize(text)  # i.e. ["filters", "-", ...]

    # 10. Align tense - Function expects TOKENS not a STRING
    tokens = [
        _to_present_tense(verb=token, corrections_dict=corrections_dict)
        for token in tokens
    ]  # i.e. [... "accumulat", ...]

    # 11. Pluralise - Function expects TOKENS not a STRING
    tokens = [
        _singularise(word=token, corrections_dict=corrections_dict)
        for token in tokens
    ]  # i.e. ["filter", "-", ...]

    # 12. Recreate _text as string based on processed tokens.
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


def _singularise(word: str, corrections_dict: dict) -> str:
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

    # Handling some irregular nouns
    irregulars = {
        "children": "child",
        "geese": "goose",
        "men": "man",
        "women": "woman",
        "teeth": "tooth",
        "feet": "foot",
        "mice": "mouse",
        "people": "person",
        "sheep": "sheep",
        "deer": "deer",
        "fish": "fish",
        "moose": "moose",
        "series": "series",
        "species": "species",
        "corps": "corps",
        "lens": "lens",
        "quizzes": "quiz",
    }

    if word in irregulars:
        return irregulars[word]

    # Ignore keywords from corrections_dict
    keywords_set = set()
    for terms in corrections_dict.values():
        words = str(terms).split()
        keywords_set.update(words)
    keywords = list(keywords_set)

    if word not in keywords:
        # Don't singularise short words (was, is, etc)
        if len(word) <= 3:
            return word

        if word.endswith("es"):
            ix_exceptions = r"^(matrices|appendices)$"
            if re.findall(
                ix_exceptions, word
            ):  # "matrices" -> "matrix", "appendices" -> "appendix"
                return word[:-3] + "x"
            ex_exceptions = r"^(indices|vertices|vortices)$"
            if re.findall(
                ex_exceptions, word
            ):  # "indices" -> "index", "vertices" -> "vertex"
                return word[:-4] + "ex"
            is_exceptions = (
                r"^(theses|analyses|crises|diagnoses|oases|parentheses|"
                r"syntheses|ellipses|hypotheses|emphases)$"
            )
            if re.findall(
                is_exceptions, word
            ):  # "theses" -> "thesis", "analyses" -> "analysis"
                return word[:-2] + "is"

            # "buses" -> "bus", "foxes" -> "fox", "bushes" -> "bush", "churches" -> "church"
            if word[-3] in ["s", "x", "z"] or word[-4:-2] in ["sh", "ch"]:
                se_exceptions = (
                    r"^(abuses|accuses|advises|analyses|arises|bases|bruises|cases|causes|ceases|"
                    r"chases|cheeses|chooses|clauses|closes|collapses|comprises|compromises|"
                    r"confuses|corpses|courses|cruises|curses|databases|decreases|defenses|"
                    r"diagnoses|diseases|doses|endoreses|enterprises|excuses|exercises|expenses|"
                    r"exposes|franchises|fuses|glimpses|horses|houses|imposes|impulses|increases|"
                    r"leases|licenses|loses|muses|noises|noses|nurses|offenses|opposes|pauses|"
                    r"phases|phrases|pleases|poses|praises|premises|promises|proposes|pulses|"
                    r"purchases|purposes|purses|raises|realises|recognises|refuses|releases|"
                    r"responses|reverses|rises|rinses|roses|senses|shocases|specialises|spouses|"
                    r"suitcases|suprises|universes|uses|vases|verses|warehouses)$"
                )
                ze_exceptions = (
                    r"^(analyzes|amazes|blazes|freezes|prizes|sizes)$"
                )
                che_exceptions = r"^(aches|headaches|niches)$"
                if (
                    re.findall(se_exceptions, word)
                    or re.findall(ze_exceptions, word)
                    or re.findall(che_exceptions, word)
                ):
                    return word[:-1]
                else:
                    return word[:-2]

            elif (
                word.endswith("ies") and len(word) > 4
            ):  # "berries" -> "berry"
                return word[:-3] + "y"

            elif word.endswith("oes"):  # "potatoes" -> "potato"
                return word[:-2]

            elif word.endswith("ves"):  # "behaves" -> "behave"
                ves_exceptions = (
                    r"^(abrasives|achieves|addictives|additives|adhesives|adjectives|"
                    r"administratives|adoptives|alternatives|approves|archives|arrives|"
                    r"automotives|aves|behaves|believes|bravescaptives|carves|captives|caves|"
                    r"cloves|collectives|comparatives|concaves|conceives|conductives|connectives|"
                    r"conserves|conservatives|coves|contraceptives|craves|cooperatives|curves|"
                    r"deceives|delves|deprives|derivatives|derives|deserves|detectives|digestives|"
                    r"directives|disapproves|dissolves|dives|doves|drives|electives|eves|evolves|"
                    r"executives|explosives|fives|forgives|formatives|fugitives|gives|gloves|"
                    r"graves|grieves|grooves|groves|heaves|hives|hoves|improves|involves|"
                    r"inventives|initiatives|jives|knaves|legislatives|locomotives|loves|"
                    r"motives|moves|narratives|natives|negatives|nerves|normatives|objectives|"
                    r"observes|octaves|olives|operatives|overdrives|oxidatives|paves|perspectives|"
                    r"perceives|positives|predictives|preserves|primitives|progressives|proves|"
                    r"raves|receives|reeves|relieves|relives|relatives|removes|reserves|"
                    r"representatives|resolves|retrieves|revives|revolves|salves|saves|serves|"
                    r"shaves|shoves|sieves|slaves|sleeves|solves|starves|staves|stoves|strives|"
                    r"suaves|survives|thrives|troves|twelves|valves|verves|waives|waves|weaves)$"
                )
                if re.findall(ves_exceptions, word):
                    return word[:-1]
                if word.endswith(
                    "ives"
                ):  # "knives" -> "knife", "wives" -> "wife"
                    return word[:-3] + "fe"
                # "leaves" -> "leaf", "halves" -> "half"
                return word[:-3] + "f"

            else:
                return word[:-1]

        elif word.endswith("a"):
            um_exceptions = r"^(data|bacteria|memoranda|strata|curricula|millennia|spectra|referenda)$"
            if re.findall(
                um_exceptions, word
            ):  # "data" -> "datum", "bacteria" -> "bacterium"
                return word[:-1] + "um"
            on_exceptions = r"^(criteria|phenomena|automata)$"
            if re.findall(on_exceptions, word):  # "criteria" -> "criterion"
                return word[:-1] + "on"

        elif word.endswith("i"):
            us_exceptions = r"^(radii|foci|fungi|nuclei|cacti|stimuli)$"
            if re.findall(us_exceptions, word):  # "radii" -> "radius"
                return word[:-1] + "us"

        # "rays" -> "ray", "boys" -> "boy"
        elif word.endswith("ys") and word[-3] in ["a", "e", "i", "o", "u"]:
            return word[:-2] + "y"

        # Handle double ss endings - "glass" -> "glass"
        elif word.endswith("ss"):
            return word

        # Handle general cases ending in s for plural
        elif word.endswith("s") and (
            word[-2] not in ["i", "u"]
        ):  # "cats" -> "cat"
            as_exceptions = r"^(alias|atlas|bias|canvas|pancreas|whereas)$"
            if re.findall(as_exceptions, word):
                return word
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
        "been": "be",
        "bled": "bleed",
        "bred": "breed",
        "brought": "bring",
        "chose": "choose",
        "fed": "feed",
        "fled": "flee",
        "led": "lead",
        "saw": "see",
        "sped": "speed",
        "threw": "throw",
        "knew": "know",
    }

    # "under" listed before "un" else will never catch "under" cases
    prefixes = r"^(re|under|un|over|dis|mis|out)"

    if verb in irregulars:
        return irregulars[verb]

    if re.findall(prefixes, verb):
        root = re.sub(prefixes, "", verb)
        if root in irregulars:
            prefix_length = len(verb) - len(root)
            return verb[:prefix_length] + irregulars[root]

    # Ignore keywords from corrections_dict
    keywords_set = set()
    for terms in corrections_dict.values():
        words = str(terms).split()
        keywords_set.update(words)
    keywords = list(keywords_set)

    stem = ""
    if verb not in keywords:
        if verb.endswith("ed"):
            stem = verb[: -len("ed")]
            # eliminating non-verbs that end in -ed
            if len(stem) <= 1:
                return verb

        elif verb.endswith("ing"):
            stem = verb[: -len("ing")]
            # eliminating non-verbs that end in -ing
            ing_non_verbs = (
                r"^(bearing|beesting|beeswing|building|cabling|ceiling|cladding|"
                r"coupling|cowling|darling|duckling|fastening|fitting|fledgling|"
                r"hamstring|hireling|inkling|lightning|missing|monitoring|morning|"
                r"outing|packing|quisling|underling|upbringing|unwilling|sapling|"
                r"shilling|sibling|siding|tailing|warning|willing|wiring)$"
            )
            if re.findall(ing_non_verbs, verb):
                return verb
        else:
            # words that do not end in -ing or -ed
            return verb

        # dealing with non-past tense words ====================
        # one syllable words, e.g. "bring" -> "bring"
        if re.findall(r"^[b-df-hj-np-tv-xz]+$", stem):
            return verb

        # dealing with one syllable root words =================
        # one syllable -ll stem, e.g. "filling" -> "fill"
        if re.findall(r"^[b-df-hj-np-tv-z]+[aeiou]ll$", stem):
            return stem

        # two syllable -ying words, e.g. "tying" -> "tie"
        if re.findall(r"^[b-df-hj-np-tv-z]ying$", verb):
            return verb[0] + "ie"

        # one syllable -yed words, e.g "dyed" -> "dye"
        if re.findall(r"^[b-df-hj-np-tv-z]yed$", verb):
            return verb[:-1]

        # one syllable -ied words, e.g "died" -> "die"
        if re.findall(r"^[b-df-hj-np-tv-z]ied$", verb):
            return verb[0] + "ie"

        # stem consists of vowel + consonant, e.g. "using" -> "use"
        if re.findall(r"^[aeiou][b-df-hj-np-tv-z]$", stem):
            return stem + "e"

        # dealing with patterns ===============================
        # verb exceptions that keep the double letter
        double_letter_ending_verbs = (
            r"^(ebb|add|superadd|odd|redd|egg|inn|err|shirr|"
            r"burr|deburr|flurr|skirr|purr|putt|vaxx)$"
        )

        # stems ending in double letters
        if re.findall(r"([b-dghjkmnp-rtv])\1$", stem) and not re.findall(
            double_letter_ending_verbs, stem
        ):  # "jogging" -> "jog"
            return stem[:-1]

        # stems ending in consonant + vowel + consonant pattern
        if re.findall(
            r"[b-df-hj-np-tv-z][aeiou][b-df-hj-npqstvz]$", stem
        ):  # "hoping" -> "hope"
            return stem + "e"

        # two vowel syllable division exceptions
        # ea exceptions
        syllable_division_exceptions = r"^(enucleat|ideat|malleat|nucleat|permeat|illaqueat|laureat|nauseat)$"
        if re.findall(syllable_division_exceptions, stem):
            return stem + "e"
        if stem.endswith("creat"):  # "recreating" -> "recreate"
            return stem + "e"
        if stem.endswith("lineat"):  # "lineating" -> "lineate"
            return stem + "e"
        if stem.endswith("caseat"):  # "caseating" -> "caseate"
            return stem + "e"

        # ia exceptions
        if stem.endswith("alias"):  # "aliasing" -> "alias"
            return stem
        if stem.endswith("bias"):  # "biasing" -> "bias"
            return stem
        # "abbreviating" -> "abbreviate". not including special case -ial, "trialing" -> "trial"
        if re.findall(r"ia[b-df-hjkmnp-tv-z]$", stem):
            return stem + "e"

        # vowel digraphs
        # aug exceptions
        if stem.endswith("aug"):  # "gauging" -> "gauge"
            return stem + "e"
        # ea exceptions
        ea_inclusions = r"^(bequeath|freath)$"
        if re.findall(ea_inclusions, stem):
            return stem
        if stem.endswith("eath"):  # "breathing" -> "breathe"
            return stem + "e"
        # ee exceptions
        ee_exclusions = r"^(teeth|seeth)$"
        if re.findall(ee_exclusions, stem):  # "teething" -> "teethe"
            return stem + "e"

        ee_ed_form = (
            r"^(agreed|decreed|demareed|disagreed|emceed|farseed|filigreed|"
            r"freed|fricasseed|garnisheed|gratineed|guaranteed|kneed|leveed|"
            r"peed|pureed|shivareed|squeegeed|squeed|teed|treed|trusteed)$"
        )
        if re.findall(
            ee_ed_form, verb
        ):  # deals with -eed exceptions, "agreed" -> "agree"
            return verb[:-1]
        if verb.endswith("eed"):  # deals with -eed non-verbs
            return verb
        # eu exceptions
        if stem.endswith("eun"):  # "reuning" -> "reune"
            return stem + "e"
        # ie exceptions
        ie_exclusions = r"^julienn$"
        if re.findall(ie_exclusions, stem):  # "julienning" -> "julienne"
            return stem + "e"
        # oo exceptions
        oo_exceptions = r"^sooge$"
        if re.findall(oo_exceptions, stem):  # "soogeing" -> "soogee"
            return stem + "e"
        # ou exceptions
        ou_exceptions = r"^(rout|misrout|rerout|douch|accouch)$"
        if re.findall(ou_exceptions, stem):  # "routing" -> "route"
            return stem + "e"
        if stem.endswith("oug"):  # "scrouging" -> "scrouge"
            return stem + "e"
        # ua exceptions
        if re.findall(r"ua[dgktr]$", stem):  # "arranging" -> "arrange"
            return stem + "e"
        # ue exceptions
        if stem == "queu":  # "queuing" -> "queue"
            return stem + "e"
        # ui exceptions
        if re.findall(r"ui[rdl]$", stem):  # "arranging" -> "arrange"
            return stem + "e"
        if stem == "requit":  # "requiting" -> "requite"
            return stem + "e"

        # going down alphabetically and dealing with exceptions
        # c
        if stem.endswith("c"):  # deals with -c, "bouncing" -> "bounce"
            return stem + "e"
        # f
        ff_exceptions = r"^(coiff|piaff)$"
        if re.findall(
            ff_exceptions, stem
        ):  # deals with -ff, "coiffing" -> "coiffe"
            return stem + "e"
        # g
        if re.findall(
            r"[rdl]g$", stem
        ):  # deals with -rg, -dg, -lg, "dodging" -> "dodge"
            return stem + "e"
        if stem.endswith("chang"):  # "changing" -> "change"
            return stem + "e"
        ranging_inclusions = r"^(boomerang|prang)$"
        if stem.endswith("rang") and not re.findall(
            ranging_inclusions, stem
        ):  # "ranging" -> "range"
            return stem + "e"
        if stem.endswith("eng"):  # "avenging" -> "avenge"
            return stem + "e"
        inging_ing_specific_inclusions = r"^(bringing|outringing|outspringing|understringing|unstringing|upspringing)$"
        inging_inclusions = r"^(ping|overstring|ring|spring|string|wring)$"
        if (
            re.findall(r"[bcf-hjkmp-rtv]ing$", stem)
            and not re.findall(inging_ing_specific_inclusions, verb)
            and not re.findall(inging_inclusions, stem)
        ):
            return stem + "e"
        unging_inclusions = r"^(dung|bung)$"
        if stem.endswith("ung") and not re.findall(unging_inclusions, stem):
            return stem + "e"
        ng_exceptions = r"^(flang|twing|spong)$"
        if re.findall(ng_exceptions, stem):
            return stem + "e"
        # i
        if verb.endswith("ied"):  # "spied" -> "spy"
            return stem[:-1] + "y"
        # l
        multisyllable_ll_verbs = (
            r"^(bankroll|bespell|booksell|bushfell|doomscroll|farewell|hairpull|handsell|"
            r"inscroll|kvell|logroll|misspell|outpoll|outpull|outroll|outsell|outswell|"
            r"outwell|outyell|oversell|outsmell|overswell|presell|reenroll|repoll|reroll|"
            r"resell|respell|steamroll|unroll|undersell|uproll|upsell|upswell|upwell)$"
        )
        if re.findall(multisyllable_ll_verbs, stem):
            return stem
        if re.findall(r"([bct]all$)|(thrall$)", stem) and not re.findall(
            r"^(caball|gimball|metall|pedastall|totall)$", stem
        ):
            return stem
        if re.findall(r"^(chandell|cordell)$", stem):
            return stem + "e"
        if stem.endswith("tell"):
            return stem
        ill_exceptions = r"^(imperill|perill|postill)$"
        if re.findall(r"[bdf-hj-np-tw-z]ill$", stem) and not re.findall(
            ill_exceptions, stem
        ):
            return stem
        if stem.endswith("ll"):
            return stem[:-1]
        # deals with consonant + l, "trembling" -> "tremble"
        if re.findall(r"[b-df-hj-np-tvz]l$", stem):
            return stem + "e"
        # r
        # deals with consonant + a/i/u vowel + r, "sparing" -> "spare"
        if re.findall(r"[b-df-hj-np-tv-z]+[aiu]r$", stem):
            return stem + "e"
        er_exclusions = r"^(adher|interfer|premier|rever)$"
        if stem in er_exclusions:
            return stem + "e"
        or_incusions = r"(color|tailor|sailor|author|anchor|vapor)$"
        or_exceptions = r"^(snor|stor|restor|bor|chokebor|rebor|counterbor)$"

        # deals with -oring that should add an e, "storing" -> "store"
        if re.findall(or_exceptions + r"|^[b-df-hj-np-tv-z]+or$", stem) or (
            re.findall(r"[ldhp]or$", stem)
            and not re.findall(or_incusions, stem)
        ):
            return stem + "e"
        if re.findall(
            r"uir$", stem
        ):  # deals with -uiring, "requiring" -> "require"
            return stem + "e"
        # s
        if stem.endswith("ss"):  # deals with -ssing, "accessing" -> "access"
            return stem
        if stem.endswith("s"):  # deals with -sing, "housing" -> "house"
            return stem + "e"
        # u
        if stem.endswith("u"):  # e.g. "subduing" -> "subdue"
            return stem + "e"
        # v
        if stem.endswith("v"):  # e.g. "solving" -> "solve"
            return stem + "e"
        # z
        z_exceptions = r"^(whizz|quizz)$"
        if re.findall(
            z_exceptions, stem
        ):  # deals with -uiring, e.g. "requiring" -> "require"
            return stem[:-1]
        if stem.endswith("zz"):  # e.g. "buzzing" -> "buzz"
            return stem
        if stem.endswith("z"):  # e.g. "buzzing" -> "buzz"
            return stem + "e"
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
    sorted_dict = dict(
        sorted(
            corrections_dict.items(),
            key=lambda x: len(str(x[0])),
            reverse=True,
        )
    )
    for incorrect, corrected in sorted_dict.items():
        incorrect, corrected = str(incorrect).lower(), str(corrected)
        replace = r"\b" + incorrect + r"\b"
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


def _add_space_around_punctuation(text: str):
    """This function will add spaces around punctuation marks,
    while preserving slashes and hyphens in certain cases.
    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    # Add spaces around punctuation marks, excluding slashes and hyphens
    modified_text = re.sub(
        r'([!"#$%&\'()*+,.:;<=>?@[\\\]^_`{|}~])', r" \1 ", text
    )

    # Add spaces around slashes (/) where appropriate
    modified_text = re.sub(
        r"((\w{3,})\s*\/\s*)(?=\w{3,})", r"\2 / ", modified_text
    )

    # Add spaces around hyphens (-) where appropriate
    modified_text = re.sub(
        r"((\w{3,})\s*-\s*)(?=\w{3,})", r"\2 - ", modified_text
    )

    return modified_text


def _remove_undesirable_chars(text: str):
    """Remove undesirable characters from the text.

    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    chars_to_keep = r"\,&\.\#\@\/-"
    return re.sub(rf"[^a-zA-Z0-9 {chars_to_keep}]", " ", text)


def _remove_duplicate_contiguous_chars(text: str):
    """Remove duplicate contiguous characters from the text.

    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    chars_to_keep = r"\,&\.\#\@\/-"
    # chars_to_remove = r"!\"#$%&'()\*\+,-./:;<=>\?@[\\\]^_`{|}~"
    return re.sub(rf"([{chars_to_keep}])\1+", r"\1", text)


def _remove_commas(text):
    """Remove commas from the text.

    Args:
        text (str): The string to modify.

    Returns:
        str: The modified string.
    """
    return text.replace(",", " ")
