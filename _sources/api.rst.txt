API Reference
============

This page provides detailed documentation for the LAPA-NG Python API, a system for phonetic transcription of Dutch text using rule-based pattern matching.

Core Components
-------------

Rules and Matchers
~~~~~~~~~~~~~~~~

The core of LAPA-NG is its rule-based matching system that converts written text into phonetic sounds.

.. py:module:: lapa_ng.rules.matchers

   Core matching functionality for phonetic transcription.

   .. py:class:: MatchResult

      Result of a successful rule match.

      :param str word: Original word being matched
      :param int start: Starting position of the match
      :param str matched: The substring that was matched
      :param str phonemes: Phonetic transcription for the matched substring
      :param str remainder: Remaining part of the word after the match

   .. py:class:: ContextualMatchResult

      Enhanced match result including rule information.

      :param MatchResult match_result: The basic match result
      :param str rule_id: Identifier of the rule that matched
      :param tuple[str, ...] rules_attempted: Tuple of rule IDs that were attempted before finding a match

   .. py:class:: Matcher(Protocol)

      Protocol defining the interface for rule matchers.

      .. py:method:: match(word: str, start: int) -> MatchResult | None

         Match a substring of a word against a specific rule.

         :param str word: The word to match against
         :param int start: Starting position in the word
         :return: MatchResult if successful, None otherwise

      .. py:property:: id -> str

         Return the unique identifier for this matcher.

   .. py:class:: RuleListMatcher(Matcher)

      A matcher that attempts to match a word against a list of rules in sequence.

      :param list[Matcher] rules: List of matchers to try in sequence

   .. py:function:: translate(word: str, part_matcher: Matcher) -> Generator[ContextualMatchResult, None, None]

      Translate a word into phonemes using the given matcher.

      This function attempts to match the entire word against the rules and yields
      a ContextualMatchResult for each match found. If no rule matches a character,
      it yields a 'silent' match with empty phonemes.

      :param str word: The word to translate
      :param Matcher part_matcher: The matcher to use for rule matching
      :return: Generator yielding ContextualMatchResult for each match or non-match

   .. py:class:: CachedTranslator

      A translator that caches results to improve performance.

      :param callable translate_func: The function to use for translation
      :param int cache_size: Maximum number of translations to cache (default: 10,000)

      .. py:method:: translate(word: str, translator: Matcher) -> Generator[ContextualMatchResult, None, None]

         Translate a word using the cached translator.

         :param str word: The word to translate
         :param Matcher translator: The matcher to use for rule matching
         :return: Generator yielding ContextualMatchResult for each match

      .. py:method:: __call__(word: str, translator: Matcher) -> Generator[ContextualMatchResult, None, None]

         Allow the translator to be called as a function.

         :param str word: The word to translate
         :param Matcher translator: The matcher to use for rule matching
         :return: Generator yielding ContextualMatchResult for each match

Rule Tables
~~~~~~~~~~

Rules can be loaded from Excel spreadsheets or CSV files.

.. py:module:: lapa_ng.rules_table.table

   Table-based rule processing functionality.

   .. py:function:: read_excel(file_path: str | Path, sheet_name: str | int | None = None) -> list[TabularRule]

      Read rules from an Excel file.

      :param file_path: Path to Excel file
      :param sheet_name: Name or index of sheet to read
      :return: List of TabularRule objects

   .. py:function:: read_csv(file_path: str | Path, field_separator: str = ',', skiprows: int = 0) -> list[TabularRule]

      Read rules from a CSV file.

      :param file_path: Path to CSV file
      :param field_separator: Character used to separate fields
      :param skiprows: Number of rows to skip at the start
      :return: List of TabularRule objects

Regex Rules
~~~~~~~~~~

Rules can be defined using regular expressions for flexible pattern matching, with support for character classes and YAML-based rule specifications.

.. py:module:: lapa_ng.rules_regex.rules

   Regular expression based rule specifications.

   .. py:class:: RegexRuleSpec

      Specification for a regular expression based rule.

      :param str id: Unique identifier for the rule
      :param re.Pattern pattern: Compiled regular expression pattern
      :param str replacement: Phonetic replacement string
      :param dict[str, Any] meta: Additional metadata about the rule

   .. py:class:: RegexMatcher(Matcher)

      A matcher that uses regular expressions for pattern matching.

      :param str id: Unique identifier for the matcher
      :param str rule: Regular expression pattern
      :param str replacement: Phonetic replacement string
      :param dict[str, Any] meta: Optional metadata about the rule

      The matcher supports the following character classes:
      - ``[:vowel:]`` - Matches any vowel (aeiouy)
      - ``[:consonant:]`` - Matches any consonant (bcdfghjklmnpqrstvwxz)
      - ``[:digit:]`` - Matches any digit (0123456789)
      - ``[:punctuation:]`` - Matches punctuation (.,!?:;)

      Rules starting with ``^`` are treated as prefix rules and only match at the start of words.
      Rules must contain a capturing group ``(pattern)`` to specify which part of the match to replace.

   .. py:function:: load_matchers(rule_file: str | Path) -> tuple[RegexMatcher, ...]

      Load regex matchers from a YAML file containing rule specifications.

      :param rule_file: Path to YAML file containing rule specifications
      :return: Tuple of RegexMatcher objects

      Example YAML format:

      .. code-block:: yaml

         - id: "rule1"
           pattern: "^([:vowel:]+)"
           replacement: "V"
           meta:
             description: "Match initial vowels"

Text Processing
-------------

NAF Processing
~~~~~~~~~~~~~

Text can be read from NAF (NLP Annotation Format) XML files using a streaming parser.

.. py:module:: lapa_ng.naf

   NAF file processing functionality.

   .. py:class:: WordForm

      Represents a word form element from a NAF file.

      :param str text: The text content of the word form
      :param dict[str, str] attributes: Dictionary of XML attributes associated with the word form

   .. py:function:: parse_naf(naf_file: str) -> Generator[WordForm, None, None]

      Parse a NAF file and yield WordForm objects.

      This function uses a streaming XML parser to efficiently process large NAF files.
      It yields WordForm objects for each word form element found in the text section.

      :param naf_file: Path to the NAF file to parse
      :return: Generator yielding WordForm objects

      Example Usage:

      .. code-block:: python

         from lapa_ng.naf import parse_naf

         # Process a NAF file efficiently
         for word_form in parse_naf("example.naf"):
             print(f"Text: {word_form.text}")
             print(f"Attributes: {word_form.attributes}")

Text Cleaning
~~~~~~~~~~~~

Text can be cleaned prior to phonetic transcription using a configurable pipeline.

.. py:module:: lapa_ng.pipeline.clean

   Text cleaning pipeline functionality.

   .. py:function:: create_pipeline(*functions: callable) -> callable

      Create a text cleaning pipeline from a sequence of cleaning functions.

      :param functions: One or more cleaning functions to apply in sequence
      :return: Combined cleaning function

   Available Cleaners:

   .. py:function:: ensure_text(text: str | None) -> str

      Ensure that the text is a string and not None. Returns an empty string if input is None.

   .. py:function:: strip_spaces(text: str) -> str

      Strip whitespace from the beginning and end of the text.

   .. py:function:: to_lowercase(text: str) -> str

      Convert the text to lowercase.

   .. py:function:: strip_accents(text: str) -> str

      Remove diacritical marks (accents) from characters in a string.

   Example Usage:

   .. code-block:: python

      from lapa_ng.pipeline.clean import (
          create_pipeline,
          ensure_text,
          strip_spaces,
          to_lowercase,
          strip_accents
      )

      # Create a pipeline that:
      # 1. Ensures text is not None
      # 2. Strips whitespace
      # 3. Converts to lowercase
      # 4. Removes accents
      cleaner = create_pipeline(
          ensure_text,
          strip_spaces,
          to_lowercase,
          strip_accents
      )

      # Use the pipeline
      cleaned_text = cleaner("  Café au Lait  ")
      # Result: "cafe au lait" 