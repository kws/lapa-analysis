from cachetools import LFUCache

from lapa_ng.rules.matchers import Matcher, MatchResult, ContextualMatchResult
from lapa_ng.rules_regex.rules import RegexMatcher


class RegexListMatcher(Matcher):
    """
    An optmised list matcher that first filters the rules based on the first letter of the word to speed up the matching process.
    """
    def __init__(self, rules: list[RegexMatcher]):
        self.rules = rules
        self.candidate_cache = LFUCache(maxsize=1000)

    def match(self, word: str, start: int) -> MatchResult | None:
        candidate_rules = self.find_candidate_rules(word, start)

        rules_attempted = []
        for rule in candidate_rules:
            match = rule.match(word, start)
            if match:
                return ContextualMatchResult(match_result = match, rule_id = rule.id, rules_attempted = tuple(rules_attempted))
            rules_attempted.append(rule.id)

    
    def find_candidate_rules(self, word: str, start: int) -> tuple[Matcher, ...]:
        """
        Find candidate rules for a given word and start position.
        This optimises the amount of rules that have to attempt for each word/part
        Currently, this optimisation is based on the assumption that we have only have regex rules,
        but it can be extended to other rule types in the future.
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
        """
        Return the id of the rule.
        """
        return f"RegexListMatcher(len={len(self.rules)})"
    
    def __repr__(self) -> str:
        return f"RegexListMatcher(len={len(self.rules)})"
    
    def __len__(self) -> int:
        return len(self.rules)
