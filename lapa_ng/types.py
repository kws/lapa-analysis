from dataclasses import dataclass, field
from typing import Generator, Iterable, Literal, Protocol, Sequence, TypeAlias


@dataclass(frozen=True)
class Word:
    """A word in the input text with optional attributes.

    This class represents a single word that needs to be transcribed phonetically.
    It can include additional attributes to help identify the word within a text.

    Attributes:
        text (str): The actual text of the word.
        attributes (dict[str, str]): Optional metadata about the word, such as position
            in text or special formatting.
    """

    text: str
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Phoneme:
    """Represents a single phoneme with its various representations.

    A phoneme is the smallest unit of sound in a language. This class provides
    multiple representations of the same phoneme for different use cases.

    Attributes:
        sampa (str): SAMPA (Speech Assessment Methods Phonetic Alphabet) representation
        ipa (str | None): International Phonetic Alphabet representation
        example (str | None): Example word containing this phoneme
        notes (str | None): Additional notes about the phoneme's usage or characteristics
    """

    sampa: str
    ipa: str | None = None
    example: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class MatchResult:
    """The result of matching a substring of a word against a rule.

    This class represents a successful match between a word and a rule pattern,
    containing information about what was matched and the resulting phonemes.

    Attributes:
        word (Word): The original word being matched
        phonemes (Sequence[Phoneme]): The phonemes produced by the match
        start (int): The starting position of the match in the word
        matched (str): The substring that was matched
        remainder (str): The remaining part of the word after the match
    """

    word: Word
    phonemes: Sequence[Phoneme]
    start: int
    matched: str
    remainder: str

    def phoneme_str(self, separator: str = " ") -> str:
        """Return a string of the phonemes separated by the given separator.

        Args:
            separator (str): The string to use as a separator between phonemes

        Returns:
            str: A string of the phonemes separated by the given separator
        """
        return separator.join(p.sampa for p in self.phonemes)


@dataclass(frozen=True)
class ContextualMatchResult(MatchResult):
    """A match result that includes information about the rules used.

    Extends MatchResult to include information about which rule was used
    and what other rules were attempted.

    Attributes:
        rule_id (str): The identifier of the rule that produced this match
        rules_attempted (tuple[str, ...]): List of rule IDs that were tried
            before finding this match
    """

    rule_id: str
    rules_attempted: tuple[str, ...]

    @classmethod
    def from_match_result(
        cls, match_result: MatchResult, rule_id: str, rules_attempted: tuple[str, ...]
    ) -> "ContextualMatchResult":
        """Create a ContextualMatchResult from a basic MatchResult.

        Args:
            match_result: The base match result to convert
            rule_id: The ID of the rule that produced the match
            rules_attempted: List of rule IDs that were tried

        Returns:
            A new ContextualMatchResult with the same match data plus rule information
        """
        return cls(
            match_result.word,
            match_result.phonemes,
            match_result.start,
            match_result.matched,
            match_result.remainder,
            rule_id,
            rules_attempted,
        )


class Matcher(Protocol):
    """Protocol defining the interface for matching words against rules.

    A matcher is responsible for finding matches between substrings of words
    and rule patterns, returning the corresponding phonetic transcriptions.

    Methods:
        match: Find matches for a word starting at a given position
    """

    def match(self, word: Word, start: int) -> Generator[MatchResult, None, None]:
        """Find matches for a word starting at a given position.

        Args:
            word: The word to match against
            start: The position in the word to start matching from

        Yields:
            MatchResult objects for each successful match found
        """
        ...


EmitValue: TypeAlias = Literal["word", "rule", "phoneme"]
"""Type alias defining the possible granularities for translation results.

This defines the different levels at which translation results can be emitted:
- "word": Results are grouped by complete words
- "rule": Results are grouped by individual rule matches
- "phoneme": Results are individual phonemes
"""


@dataclass
class TranslationResult:
    """The result of translating a word into phonemes.

    This class represents the complete translation of a word, including
    all phonemes and the match results that produced them.

    Attributes:
        word (Word): The original word being translated
        phonemes (Sequence[Phoneme]): The complete set of phonemes for the word
        match_results (Sequence[MatchResult]): The sequence of matches that
            produced the phonemes
    """

    word: Word
    phonemes: Sequence[Phoneme]
    match_results: Sequence[MatchResult]

    def phoneme_str(self, separator: str = " ") -> str:
        """Return a string of the phonemes separated by the given separator.

        Args:
            separator (str): The string to use as a separator between phonemes

        Returns:
            str: A string of the phonemes separated by the given separator
        """
        return separator.join(p.sampa for p in self.phonemes)


WordOrWordList: TypeAlias = Word | Iterable[Word]
"""Type alias for either a single word or a collection of words.

This type is used to allow translation functions to accept either a single
word or multiple words as input.
"""


class Translator(Protocol):
    """Protocol defining the interface for translating words into phonemes.

    A translator is responsible for converting words into their phonetic
    representations using a set of rules and patterns.

    Methods:
        translate: Convert words into their phonetic representations
    """

    def translate(
        self, word: WordOrWordList, *, emit: EmitValue | None
    ) -> Generator[TranslationResult, None, None]:
        """Translate words into their phonetic representations.

        Args:
            word: The word or words to translate
            emit: The granularity at which to emit results (word, rule, or phoneme)

        Yields:
            TranslationResult objects containing the phonetic translations
        """
        ...
