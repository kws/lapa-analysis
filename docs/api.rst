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

   .. py:class:: Matcher(Protocol)

      Protocol defining the interface for rule matchers.

      .. py:method:: match(word: str, start: int) -> MatchResult | None

         Match a substring of a word against a specific rule.

         :param str word: The word to match against
         :param int start: Starting position in the word
         :return: MatchResult if successful, None otherwise

   .. py:class:: MatchResult

      Result of a successful rule match.

      :param str word: Original word being matched
      :param int start: Starting position of the match
      :param str matched: The substring that was matched
      :param str phonemes: Phonetic transcription for the matched substring
      :param str remainder: Remaining part of the word after the match

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

Rules can be defined using regular expressions for flexible pattern matching.

.. py:module:: lapa_ng.rules_regex.rules

   Regular expression based rule specifications.

   .. py:class:: RegexMatcher(Matcher)

      A matcher that uses regular expressions for pattern matching.

      :param str id: Unique identifier for the matcher
      :param str rule: Regular expression pattern
      :param str replacement: Phonetic replacement string
      :param dict meta: Additional metadata

   .. py:function:: load_matchers(rule_file: str | Path) -> tuple[RegexMatcher, ...]

      Load regex matchers from a rule file.

      :param rule_file: Path to rule specification file
      :return: Tuple of RegexMatcher objects

Text Processing
-------------

NAF Processing
~~~~~~~~~~~~~

Text can be read from NAF (NLP Annotation Format) XML files.

.. py:module:: lapa_ng.naf

   NAF file processing functionality.

   .. py:function:: read_naf(naf_file: str | Path) -> str

      Read text content from a NAF XML file.

      :param naf_file: Path to NAF XML file
      :return: Extracted text content

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