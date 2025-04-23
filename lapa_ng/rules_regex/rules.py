"""
Regular expression rule specifications and matchers for LAPA-NG.

This module provides classes and functions for working with regular expression
based rules for phonetic transcription.
"""

from pathlib import Path
import re
from typing import Any
from lapa_ng.rules.matchers import Matcher, MatchResult
from dataclasses import dataclass
import yaml

DEFAULT_CHARACTER_CLASSES = {
    "vowel": "aeiouy",
    "consonant": "bcdfghjklmnpqrstvwxz",
    "digit": "0123456789",
    "punctuation": ".,!?:;",
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
    pattern: re.Pattern
    replacement: str
    meta: dict[str, Any]
    

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

    __slots__ = ('id', 'replacement', 'match_group', 'prefix', 'rule')
    
    def __init__(self, id: str, rule: str, replacement: str, meta: dict[str, Any] = None):
        """Initialize a new regex matcher.
        
        Args:
            id: Unique identifier for the matcher
            rule: The regular expression pattern
            replacement: The phonetic replacement string
            meta: Optional metadata about the rule
            
        Raises:
            ValueError: If no match group is found in the rule
        """
        self.id = id
        self.replacement = replacement
        self.meta = meta

        # For optimisation, we extract the match group from the rule.
        match = re.search(r'\((.*)\)', rule)
        if match:
            self.match_group = match.group(1)
        else:
            raise ValueError(f"No match group found in rule {self.id}: {rule}")

        # If the rule starts with a caret, it is a prefix rule. We only then match for start == 0
        if rule.startswith('^'):
            self.prefix = True
            self.rule = rule
        else:
            self.prefix = False
            self.rule = '^' + rule

        # Replace the character classes with the actual characters
        for class_name, characters in DEFAULT_CHARACTER_CLASSES.items():
            self.rule = re.sub(rf"\[:{class_name}:\]", f"[{characters}]", self.rule)

        self.rule = re.compile(self.rule)

    def match(self, word: str, start:int) -> MatchResult | None:
        """Attempt to match the rule against a word starting at the given position.
        
        Args:
            word: The word to match against
            start: Starting position in the word
            
        Returns:
            MatchResult if the rule matches, None otherwise
        """
        if self.prefix and start != 0:
            return None

        test_word = word[start:]
        match = self.rule.match(test_word)
        if not match:
            return None

        replacement_part = match.group(1)
        replacment_length = len(replacement_part)

        remainder = word[start + replacment_length:]

        return MatchResult(matched = replacement_part, phonemes = self.replacement, word = word, start = start, remainder = remainder)


def load_specs(rule_file: str | Path) -> tuple[RegexRuleSpec, ...]:
    """Load rule specifications from a YAML file.
    
    Args:
        rule_file: Path to the YAML file containing rule specifications
        
    Returns:
        Tuple of RegexRuleSpec objects created from the file
    """
    with open(rule_file, 'r') as f:
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
