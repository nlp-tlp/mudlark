Implementation
==============

Simple Normalisation
--------------------

This section outlines the steps involved in the normalisation process performed by the ``simple_normalise`` function.

**Normalization Steps:**

1. **Lowercase Text:** Convert the entire text to lowercase.
2. **Remove Commas:** Eliminate commas from the text.
3. **Remove duplicate contiguous characters:** Remove duplicate contiguous characters from the text.
4. **Add Space Around Punctuations:** Ensures there are spaces around punctuations in the text.
5. **Anonymise Sentence:** Anonymise the sentence, replacing sensitive information.
6. **Remove Extra Spaces:** Eliminate any extra spaces between words.
7. **Fix Typos:** Correct typos using the corrections dictionary.
8. **Tokenise:** Tokenise the text into a list of words.
9. **Align Tenses to Present Tense:** Adjust verb tenses to present tense using ``_to_present_tense``.
10. **Convert Nouns to Singular Form:** Singularise words using ``_singularise``.
11. **Recreate Text from Tokens:** Reconstruct the normalised text based on processed tokens.

For more detailed information on each step, please refer below.

Fix Typos
^^^^^^^^^

This step involves correcting typos in a given text based on a provided mapping dictionary.

.. list-table::
    :widths: 30 30
    :header-rows: 1

    * - Original Text
      - Corrected Text
    * - pummp is Broken
      - pump is Broken
    * - a/c leakin
      - air conditioner leak
    * - wall was craked
      - wall was cracked

Anonymise Sentence
^^^^^^^^^^^^^^^^^^
This function anonymises a given sentence by replacing potential asset identifiers with the placeholder "AssetID". 

The pattern used to identify asset identifiers is defined as follows:

- **b:** Represents a word boundary, ensuring that the pattern is treated as a distinct word.
- **[A-Za-z]*:** Matches zero or more alphabetical characters, covering cases where an asset identifier might start with letters.
- **\d+:** Matches one or more numeric characters, ensuring patterns with numbers are identified.
- **[A-Za-z]*:** Matches zero or more alphabetical characters, covering cases where an asset identifier might end with letters.
- **b:** Another word boundary to ensure the end of the matched pattern is treated as a distinct word.

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
This section describes the manual steps involved in the ``singularise`` function for converting words to singular form.

1. Pass through all words listed in the corrections dictionary.
2. Short words (3 letters or fewer) are not singularised.
3. Words ending in "es" are handled based on specific rules:

      - Special case words ending in -ices changes to either -ex or -ix based on specific cases. e.g., indices => index, matrices => matrix
      - Special case words ending in -ses change to -sis. e.g., analyses => analysis
      - Words ending in -ses, -xes, -zes, -ches or -shes drop the "es". e.g., boxes => box
      - Words ending in -ies and having a length greater than 4 change to -y. e.g., families => family
      - Words ending in -oes drop the "es". e.g., potatoes => potato
      - Words ending in -ives change to -fe. e.g., knives => knife
      - Words ending in -ves change to -f. e.g., leaves => leaf
      - Exception words ending in -ves. e.g., "detectives" => "detective"
      - Other words ending in -es drop the "s".
4. Dealing with plural words ending in -a:
      
      - Special case words ending in -a change to -um. e.g., data => datum
      - Special case words ending in -a change to -on. e.g., criteria => criterion
5. Dealimg with plural words endding in -i:
      
      - Words ending in -i change to -us. e.g., radii => radius
6. Words ending in -ys and preceded by a vowel change to -y. e.g., boys => boy
7. Words ending in -ss remain unchanged after dropping "es". e.g., glass => glass
8. Words ending in -s and not preceded by "u" or "i" drop the "s".
      
      - Example: cars => car, dogs => dog, radius => radius, tennis => tennis
      - Exceptions: nouns that end in -as