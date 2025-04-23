
from dataclasses import dataclass
from typing import Callable, Generator, Protocol
from cachetools import LFUCache

@dataclass
class MatchResult:
    word: str
    start: int
    matched: str
    phonemes: str
    remainder: str

@dataclass
class ContextualMatchResult:
    match_result: MatchResult
    rule_id: str
    rules_attempted: tuple[str, ...]


class Matcher(Protocol):

    def match(self, word: str, start:int) -> MatchResult | None:
        """
        Return a MatchResult if the rule matches, None otherwise.
        """

    @property
    def id(self) -> str:
        """
        Return the id of the rule.
        """
        ...

class RuleListMatcher(Matcher):
    """
    A class that matches a word against a list of rules returning 
    """
    def __init__(self, rules: list[Matcher]):
        self.rules = rules

    def match(self, word: str, start: int) -> MatchResult | None:
        """
        A helper function that matches a word against a list of rules.
        It will return the first match it finds, the rule that matched, and the rules it attempted to match.
        """
        rules_attempted = []
        for rule in self.rules:
            match = rule.match(word, start)
            if match:
                return ContextualMatchResult(match_result = match, rule_id = rule.id, rules_attempted = tuple(rules_attempted))
            rules_attempted.append(rule.id)

    @property
    def id(self) -> str:
        """
        Return the id of the rule.
        """
        return f"RuleListMatcher(len={len(self.rules)})"


def translate(word: str, part_matcher: Matcher) -> Generator[ContextualMatchResult, None, None]:
    """
    A basic, unoptimised match function that matches a word against a list of rules.
    It will attempt to match the entire word agains the rules and yield a ContextualMatchResult for each match found. 
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

        # In the case of no match, we yield a 'silent' match.
        matched = word_remainder[0]
        word_remainder = word_remainder[1:]

        match_result = MatchResult(matched = matched, phonemes = '', word = word, start = current_pos, remainder = word_remainder)
        yield ContextualMatchResult(match_result = match_result, rule_id = "NO_MATCH", rules_attempted = tuple([part_matcher.id]))


class CachedTranslator:
    """
    A class that caches the results of a translator.
    """
    def __init__(self, translate_func, cache_size: int = 10_000):
        self.cache = LFUCache(maxsize=cache_size)
        self.translate_func = translate_func

    def translate(self, word: str, translator: Matcher) -> Generator[ContextualMatchResult, None, None]:
        value = self.cache.get(word)
        if value:
            yield from value
            return

        t = tuple(self.translate_func(word, translator))
        self.cache[word] = t
        yield from t

    def __call__(self, word: str, translator: Matcher) -> Generator[ContextualMatchResult, None, None]:
        return self.translate(word, translator)
