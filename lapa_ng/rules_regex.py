"""
Regular expression rule specifications and matchers for LAPA-NG.

This module provides classes and functions for working with regular expression
based rules for phonetic transcription.

Optimized rule matching for regular expression based rules.

This module provides an optimized implementation of rule matching that
uses caching and filtering to improve performance.

"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator, Mapping, Sequence

import yaml
from cachetools import LFUCache

from lapa_ng.types import ContextualMatchResult, Matcher, MatchResult, Phoneme, Word

DEFAULT_CHARACTER_CLASSES = {
    "vowel": "aeiouy",
    "consonant": "bcdfghjklmnpqrstvwxz",
    "digit": "0123456789",
}


@dataclass(frozen=True)
class RegexRuleSpec:
    """Specification for a regular expression based rule.

    This class encapsulates all the information needed to create a RegexMatcher,
    including the pattern, replacement, and metadata.

    Attributes:
        id: Unique identifier for the rule
        pattern: Compiled regular expression pattern
        replacement: Phonetic replacement string
        meta: Additional metadata about the rule
    """

    id: str
    pattern: str
    replacement: Sequence[Phoneme]
    meta: Mapping[str, Any] = field(default_factory=dict)

    def asdict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation of the rule specification."""
        return {
            "id": self.id,
            "pattern": self.pattern,
            "replacement": [p.sampa for p in self.replacement],
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RegexRuleSpec":
        """Create a RegexRuleSpec from a dictionary."""
        return cls(
            id=data["id"],
            pattern=[Phoneme(v) for v in data["pattern"]],
            replacement=[Phoneme(sampa=p) for p in data["replacement"]],
            meta=data.get("meta", {}),
        )


class RegexMatcher(Matcher):
    """A matcher that uses regular expressions for pattern matching.

    This class implements the Matcher protocol using regular expressions.
    It includes optimizations for prefix rules and match group extraction.

    Attributes:
        id: Unique identifier for the matcher
        replacement: Phonetic replacement string
        match_group: The capturing group in the regex pattern
        prefix: Whether the rule must match at the start of the word
        rule: The compiled regular expression pattern
    """

    __slots__ = ("id", "replacement", "match_group", "prefix", "rule")

    def __init__(
        self,
        spec: RegexRuleSpec,
        character_classes: dict[str, str] = DEFAULT_CHARACTER_CLASSES,
    ):
        """Initialize a new regex matcher.

        Args:
            id: Unique identifier for the matcher
            rule: The regular expression pattern
            replacement: The phonetic replacement strings
            meta: Optional metadata about the rule

        Raises:
            ValueError: If no match group is found in the rule
        """
        self.id = spec.id
        self.replacement = tuple(spec.replacement)
        self.meta = spec.meta

        for ph in self.replacement:
            assert isinstance(
                ph, Phoneme
            ), f"Replacements must be of type Phoneme, but got {type(ph)}"

        # For optimisation, we extract the match group from the rule.
        match = re.search(r"\((.*)\)", spec.pattern)
        if match:
            self.match_group = match.group(1)
        else:
            raise ValueError(f"No match group found in rule {self.id}: {spec.pattern}")

        # If the rule starts with a caret, it is a prefix rule. We only then match for start == 0
        if spec.pattern.startswith("^"):
            self.prefix = True
            self.rule = spec.pattern
        else:
            self.prefix = False
            self.rule = "^" + spec.pattern

        # Replace the character classes with the actual characters
        for class_name, characters in character_classes.items():
            self.rule = re.sub(rf"\[:{class_name}:\]", f"[{characters}]", self.rule)

        self.rule = re.compile(self.rule)

    def match(self, word: Word, start: int) -> Generator[MatchResult, None, None]:
        """Attempt to match the rule against a word starting at the given position.

        Args:
            word: The word to match against
            start: Starting position in the word

        Returns:
            MatchResult if the rule matches, None otherwise
        """
        if self.prefix and start != 0:
            return []

        test_word = word.text[start:]
        match = self.rule.match(test_word)
        if not match:
            return []

        replacement_part = match.group(1)
        replacment_length = len(replacement_part)

        remainder = word.text[start + replacment_length :]

        yield MatchResult(
            matched=replacement_part,
            phonemes=self.replacement,
            word=word,
            start=start,
            remainder=remainder,
        )

    @property
    def spec(self) -> RegexRuleSpec:
        """Return the specification for the rule."""
        return RegexRuleSpec(
            id=self.id,
            pattern=self.rule.pattern,
            replacement=self.replacement,
            meta=self.meta,
        )


class RegexListMatcher(Matcher):
    """An optimized list matcher for regex-based rules.

    This class implements the Matcher protocol with optimizations for regex rules.
    It uses caching and filtering based on the first letter of the word to
    reduce the number of rules that need to be attempted.
    """

    def __init__(self, rules: list[RegexMatcher]):
        """Initialize with a list of regex matchers.

        Args:
            rules: List of regex matchers to use
        """
        self.rules = rules
        self.candidate_cache = LFUCache(maxsize=1000)

    def match(
        self, word: Word, start: int
    ) -> Generator[ContextualMatchResult, None, None]:
        """Attempt to match the word against the candidate rules.

        Args:
            word: The word to match against
            start: Starting position in the word

        Returns:
            ContextualMatchResult if a match is found, None otherwise
        """
        candidate_rules = self.find_candidate_rules(word, start)

        rules_attempted = []
        for rule in candidate_rules:
            match_results = list(rule.match(word, start))
            if match_results:
                for mr in match_results:
                    yield ContextualMatchResult.from_match_result(
                        mr, rule.id, rules_attempted
                    )
                return
            rules_attempted.append(rule.id)

    def find_candidate_rules(self, word: Word, start: int) -> tuple[Matcher, ...]:
        """Find candidate rules that might match the word at the given position.

        This method optimizes matching by:
        1. Filtering rules based on the first letter of the word
        2. Considering prefix rules only at the start of the word
        3. Caching results to avoid recomputation

        Args:
            word: The word to match against
            start: Starting position in the word

        Returns:
            Tuple of candidate matchers that might match the word
        """
        test_letter = word.text[start]
        is_prefix = start == 0

        if (test_letter, is_prefix) in self.candidate_cache:
            return self.candidate_cache[(test_letter, is_prefix)]

        matched_rules = []

        for rule in self.rules:
            assert isinstance(
                rule, RegexMatcher
            ), f"This optimisation currently only works with regex matchers, but got {type(rule)}"
            if rule.prefix and not is_prefix:
                continue
            if rule.match_group[0] == test_letter:
                matched_rules.append(rule)

        matched_rules = tuple(matched_rules)
        self.candidate_cache[(test_letter, is_prefix)] = matched_rules
        return matched_rules

    @property
    def id(self) -> str:
        """Return a string identifier for this matcher."""
        return f"RegexListMatcher(rules={len(self.rules)})"

    def __repr__(self) -> str:
        """Return a string representation of this matcher."""
        return f"RegexListMatcher(rules={len(self.rules)})"

    def __len__(self) -> int:
        """Return the number of rules in this matcher."""
        return len(self.rules)


def load_specs(rule_file: str | Path) -> tuple[RegexRuleSpec, ...]:
    """Load rule specifications from a YAML file.

    Args:
        rule_file: Path to the YAML file containing rule specifications

    Returns:
        Tuple of RegexRuleSpec objects created from the file
    """
    with open(rule_file, "r") as f:
        rules = yaml.safe_load(f)

    return tuple([RegexRuleSpec(**rule) for rule in rules])


def load_matchers(rule_file: str | Path) -> tuple[RegexMatcher, ...]:
    """Load and create regex matchers from a YAML file.

    Args:
        rule_file: Path to the YAML file containing rule specifications

    Returns:
        Tuple of RegexMatcher objects created from the specifications
    """
    return tuple([RegexMatcher(spec) for spec in load_specs(rule_file)])
