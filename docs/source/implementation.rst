Implementation
==============

Simple Normalisation
--------------------

This section outlines the steps involved in the normalisation process performed by the ``simple_normalise`` function.

**Normalization Steps:**

1. **Fix Typos:** Correct typos using the corrections dictionary.
2. **Lowercase Text:** Convert the entire text to lowercase.
3. **Add Space Around Hyphen:** Ensure there is a space around hyphens in the text.
4. **Remove Commas:** Eliminate commas from the text.
5. **Add Space Around Slash:** Insert spaces around slashes in the text.
6. **Anonymise Sentence:** Anonymise the sentence, replacing sensitive information.
7. **Remove Extra Spaces:** Eliminate any extra spaces between words.
8. **Tokenise:** Tokenise the text into a list of words.
9. **Align Tenses to Present Tense:** Adjust verb tenses to present tense using ``_to_present_tense``.
10. **Convert Nouns to Singular Form:** Singularise words using ``_singularise``.
11. **Recreate Text from Tokens:** Reconstruct the normalised text based on processed tokens.

For more detailed information on each step, please refer below.

Fix Typos
^^^^^^^^^
...

Lowercase Text
^^^^^^^^^^^^^^
...

Add Space Around Hyphen
^^^^^^^^^^^^^^^^^^^^^^^
...

Remove Commas
^^^^^^^^^^^^^
...

Add Space Around Slash
^^^^^^^^^^^^^^^^^^^^^^
...

Anonymise Sentence
^^^^^^^^^^^^^^^^^^
...

Remove Extra Spaces
^^^^^^^^^^^^^^^^^^^
...

Tokenise
^^^^^^^^
...

Align Tenses to Present Tense
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This section describes the manual steps involved in the ``to_present_tense`` function for normalizing words to present tense.

1. Pass through all words listed in the corrections dictionary.
2. If a word ends in -ing or -ed, pass through words listed as non-verbs.
3. Obtain the stem form by removing the -ing or -ed endings.
4. If the original word is one syllable (the stem consists only of consonants), it is passed through.
5. Dealing with One-Syllable Root Words:
      - One-syllable -ll stems
      - Two-syllable -ying words
      - One-syllable -yed words
      - One-syllable -ied words
      - Stem consists of vowel + consonant
6. Dealing with Patterns Applying Over Most Letters:
      - Verbs ending in double consonant letters typically drop the last letter.
         - Example: hopping/hopped => hop
         - Exceptions: -ff, -ll, -ss, -zz
      - Verbs ending in consonant + vowel + consonant pattern add an "e" to the stem.
         - Example: hoping/hoped => hope
         - Exceptions: -r, -w, -x, -y
7. Dealing with Two Vowel Syllable Division Exceptions:
      - Handle cases when vowel sounds remain distinct.
8. Dealing with Vowel Digraphs Exceptions:
      - Handle cases when vowel sounds blend together.
9. Alphabetical Handling of Exceptions:
      - Go down exceptions alphabetically from the end of the stem word.
      - Deal with double letters -ff, -ll, -ss, and -zz.

Convert Nouns to Singular Form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
...

Recreate Text from Tokens
^^^^^^^^^^^^^^^^^^^^^^^^^
...
