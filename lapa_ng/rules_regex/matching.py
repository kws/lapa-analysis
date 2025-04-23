"""
Optimized rule matching for regular expression based rules.

This module provides an optimized implementation of rule matching that
uses caching and filtering to improve performance.
"""

from cachetools import LFUCache

from lapa_ng.rules.matchers import Matcher, MatchResult, ContextualMatchResult
from lapa_ng.rules_regex.rules import RegexMatcher


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

    def match(self, word: str, start: int) -> MatchResult | None:
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
            match = rule.match(word, start)
            if match:
                return ContextualMatchResult(match_result = match, rule_id = rule.id, rules_attempted = tuple(rules_attempted))
            rules_attempted.append(rule.id)

    
    def find_candidate_rules(self, word: str, start: int) -> tuple[Matcher, ...]:
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
        test_letter = word[start]
        is_prefix = start == 0

        if (test_letter, is_prefix) in self.candidate_cache:
            return self.candidate_cache[(test_letter, is_prefix)]

        matched_rules = []

        for rule in self.rules:
            assert isinstance(rule, RegexMatcher), "This optimisation currently only works with regex matchers"
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
        return f"RegexListMatcher(len={len(self.rules)})"
    
    def __repr__(self) -> str:
        """Return a string representation of this matcher."""
        return f"RegexListMatcher(len={len(self.rules)})"
    
    def __len__(self) -> int:
        """Return the number of rules in this matcher."""
        return len(self.rules)
