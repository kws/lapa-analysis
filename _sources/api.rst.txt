API Reference
============

This page provides detailed documentation for the LAPA-NG Python API, a system for phonetic transcription of Dutch text using rule-based pattern matching.

Core Components
-------------

The LAPA-NG system is built around several core components that work together to perform phonetic transcription:

Translator
~~~~~~~~~

The ``Translator`` protocol defines the interface for translating words into phonemes. It provides a single method:

.. code-block:: python

    def translate(self, word: WordOrWordList, *, emit: EmitValue | None) -> Generator[TranslationResult, None, None]

The translator can process either a single word or a list of words, and can emit results at different granularities (word, rule, or phoneme level).

Matcher
~~~~~~~

The ``Matcher`` protocol defines how to match substrings of words against rules and return corresponding phonetic transcriptions:

.. code-block:: python

    def match(self, word: Word, start: int) -> Generator[MatchResult, None, None]

Implementations
~~~~~~~~~~~~~

The system provides several concrete implementations:

- ``MatchingTranslator``: A translator that uses a matcher to translate words into phonemes
- ``CachedTranslator``: A translator wrapper that caches results to improve performance

Data Types
~~~~~~~~~

The system uses several key data types:

- ``Word``: Represents a single word with optional attributes
- ``Phoneme``: Represents a single phoneme with various representations (SAMPA, IPA)
- ``MatchResult``: Contains the result of a successful rule match
- ``TranslationResult``: Contains the final translation result for a word

Rule Systems
-----------

LAPA-NG supports two complementary rule systems for phonetic transcription:

Table Rules
~~~~~~~~~~

The table rules system provides a user-friendly way to define phonetic transcription rules using tabular data (e.g., Excel spreadsheets). This system is designed to be more accessible to linguists and phoneticians who may not be familiar with regular expressions.

Key Components:

- ``TabularRule``: Represents a single rule from a tabular data source
  - ``rule_id``: Unique identifier for the rule
  - ``rule_class``: Type of rule (VOWEL, CONSONANT, or PREFIX)
  - ``letter``: Initial letter that the rule applies to
  - ``priority``: Priority value for rule ordering
  - ``description``: Human-readable description of the rule
  - ``rule``: The rule pattern or definition
  - ``replaced``: Letter sequence to be replaced
  - ``replaceby``: Replacement letter sequence

- ``RuleClass``: Enumeration of rule types
  - ``VOWEL``: Rules for vowel sounds
  - ``CONSONANT``: Rules for consonant sounds
  - ``PREFIX``: Rules for prefix patterns

The table rules system provides utilities for:
- Loading rules from tabular data sources
- Converting tabular rules to regex specifications
- Sorting rules by priority
- Checking for duplicate priorities
- Creating matchers from tabular rules

Regex Rules
~~~~~~~~~~

The regex rules system provides a more powerful and flexible way to define phonetic transcription rules using regular expressions. This system is used internally to implement the actual matching logic.

Key Components:

- ``RegexRuleSpec``: Specification for a regular expression based rule
  - ``id``: Unique identifier for the rule
  - ``pattern``: Compiled regular expression pattern
  - ``replacement``: Phonetic replacement string
  - ``meta``: Additional metadata about the rule

- ``RegexMatcher``: A matcher that uses regular expressions for pattern matching
  - Optimized for prefix rules and match group extraction
  - Supports character classes for common patterns
  - Includes caching for improved performance

- ``RegexListMatcher``: An optimized list matcher for regex-based rules
  - Uses caching and filtering based on the first letter
  - Reduces the number of rules that need to be attempted
  - Maintains rule ordering and priority

The regex rules system provides functions for:
- Loading rule specifications from YAML files
- Creating matchers from rule specifications
- Optimizing rule matching performance

Command-Line Interface
--------------------

LAPA-NG provides a command-line interface for common operations:

Converting Rules
~~~~~~~~~~~~~~

Convert Excel-based rules to YAML format:

.. code-block:: bash

    lapa convert-excel rules.xlsx rules.yaml
    # Optional: specify a particular sheet
    lapa convert-excel rules.xlsx rules.yaml --sheet "RULES"

This command reads rules from an Excel file and converts them to YAML format,
which can be used directly with the regex rules system.

Transcribing Text
~~~~~~~~~~~~~~~

Transcribe words from the command line:

.. code-block:: bash

    lapa translate-words rules.xlsx word1 word2 word3
    # Optional: specify a particular sheet
    lapa translate-words rules.xlsx word1 word2 word3 --sheet "RULES"

This command transcribes one or more words using the specified rules and outputs
the phonetic transcription in SAMPA format.

Processing NAF Files
~~~~~~~~~~~~~~~~~~

Process text from NAF (NLP Annotation Framework) files:

.. code-block:: bash

    lapa translate-naf input.naf rules.xlsx
    # Optional: specify a particular sheet
    lapa translate-naf input.naf rules.xlsx --sheet "RULES"

This command reads text from a NAF file, transcribes it using the specified rules,
and outputs the results in CSV format with detailed information about each
transcription, including:
- Word ID and text
- Position in the word
- Matched pattern
- Phoneme in SAMPA format
- Rule ID used
- Number of rules attempted

Testing
~~~~~~~

Run the test suite:

.. code-block:: bash

    lapa test

This command runs the test suite to verify the system is working correctly.

Usage Example
------------

Here's a complete example of how the components work together:

1. Define rules in an Excel spreadsheet with columns for:
   - Rule ID
   - Rule class (VOWEL, CONSONANT, PREFIX)
   - Letter
   - Priority
   - Description
   - Rule pattern
   - Replacement pattern

2. Convert the rules to YAML format:
   .. code-block:: bash
      lapa convert-excel rules.xlsx rules.yaml

3. Use the rules to transcribe text:
   .. code-block:: bash
      lapa translate-words rules.xlsx "voorbeeld" "taal"
      # Output: v r o n d @ r b @ l t a l

4. Process a NAF file:
   .. code-block:: bash
      lapa translate-naf document.naf rules.xlsx > transcriptions.csv

The system will:
1. Load and validate the rules
2. Convert them to an optimized regex-based format
3. Process the input text
4. Apply the rules in the correct order
5. Output the phonetic transcriptions

