"""
Rule matching and translation functionality for LAPA-NG.

This module provides classes and functions for matching words against rules
and performing phonetic transcription based on those rules.
"""

from dataclasses import dataclass
from typing import Callable, Generator, Protocol
from cachetools import LFUCache

@dataclass
class MatchResult:
    """Result of a successful rule match.
    
    Attributes:
        word: The original word being matched
        start: Starting position of the match in the word
        matched: The substring that was matched
        phonemes: The phonetic transcription for the matched substring
        remainder: The remaining part of the word after the match
    """
    word: str
    start: int
    matched: str
    phonemes: str
    remainder: str

@dataclass
class ContextualMatchResult:
    """Enhanced match result including rule information.
    
    Attributes:
        match_result: The basic match result
        rule_id: Identifier of the rule that matched
        rules_attempted: Tuple of rule IDs that were attempted before finding a match
    """
    match_result: MatchResult
    rule_id: str
    rules_attempted: tuple[str, ...]


class Matcher(Protocol):
    """Protocol defining the interface for rule matchers.
    
    A matcher is responsible for matching a substring of a word against a specific rule
    and returning the corresponding phonetic transcription if successful.
    """

    def match(self, word: str, start:int) -> MatchResult | None:
        """Attempt to match a rule against a word starting at the given position.
        
        Args:
            word: The word to match against
            start: Starting position in the word
            
        Returns:
            MatchResult if the rule matches, None otherwise
        """

    @property
    def id(self) -> str:
        """Return the unique identifier for this matcher."""
        ...

class RuleListMatcher(Matcher):
    """A matcher that attempts to match a word against a list of rules in sequence.
    
    This class implements the Matcher protocol by trying each rule in its list
    until a match is found or all rules have been attempted.
    """
    def __init__(self, rules: list[Matcher]):
        """Initialize with a list of rules to try.
        
        Args:
            rules: List of matchers to try in sequence
        """
        self.rules = rules

    def match(self, word: str, start: int) -> MatchResult | None:
        """Try to match the word against each rule in sequence.
        
        Args:
            word: The word to match against
            start: Starting position in the word
            
        Returns:
            ContextualMatchResult containing the first successful match and attempted rules
        """
        rules_attempted = []
        for rule in self.rules:
            match = rule.match(word, start)
            if match:
                return ContextualMatchResult(match_result = match, rule_id = rule.id, rules_attempted = tuple(rules_attempted))
            rules_attempted.append(rule.id)

    @property
    def id(self) -> str:
        """Return a string identifier for this rule list matcher."""
        return f"RuleListMatcher(len={len(self.rules)})"


def translate(word: str, part_matcher: Matcher) -> Generator[ContextualMatchResult, None, None]:
    """Translate a word into phonemes using the given matcher.
    
    This function attempts to match the entire word against the rules and yields
    a ContextualMatchResult for each match found. If no rule matches a character,
    it yields a 'silent' match with empty phonemes.
    
    Args:
        word: The word to translate
        part_matcher: The matcher to use for rule matching
        
    Yields:
        ContextualMatchResult for each match or non-match in the word
    """
    word_remainder = word
    start_length = len(word)

    while word_remainder:
        current_length = len(word_remainder)
        current_pos = start_length - current_length

        matched = part_matcher.match(word = word, start = current_pos)
        if matched:
            yield matched
            word_remainder = matched.match_result.remainder
            continue

        matched = word_remainder[0]
        word_remainder = word_remainder[1:]

        match_result = MatchResult(matched = matched, phonemes = '', word = word, start = current_pos, remainder = word_remainder)
        yield ContextualMatchResult(match_result = match_result, rule_id = "NO_MATCH", rules_attempted = tuple([part_matcher.id]))


class CachedTranslator:
    """A translator that caches results to improve performance.
    
    This class wraps a translation function and caches its results to avoid
    recomputing translations for the same words.
    """
    def __init__(self, translate_func, cache_size: int = 10_000):
        """Initialize with a translation function and cache size.
        
        Args:
            translate_func: The function to use for translation
            cache_size: Maximum number of translations to cache
        """
        self.cache = LFUCache(maxsize=cache_size)
        self.translate_func = translate_func

    def translate(self, word: str, translator: Matcher) -> Generator[ContextualMatchResult, None, None]:
        """Translate a word using the cached translator.
        
        Args:
            word: The word to translate
            translator: The matcher to use for rule matching
            
        Yields:
            ContextualMatchResult for each match in the word
        """
        value = self.cache.get(word)
        if value:
            yield from value
            return

        t = tuple(self.translate_func(word, translator))
        self.cache[word] = t
        yield from t

    def __call__(self, word: str, translator: Matcher) -> Generator[ContextualMatchResult, None, None]:
        """Allow the translator to be called as a function.
        
        Args:
            word: The word to translate
            translator: The matcher to use for rule matching
            
        Yields:
            ContextualMatchResult for each match in the word
        """
        return self.translate(word, translator)
