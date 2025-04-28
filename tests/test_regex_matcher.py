from typing import Generator
from unittest.mock import Mock

from lapa_ng.rules_regex import (
    RegexListMatcher,
)
from lapa_ng.rules_regex import RegexMatcher as _RegexMatcher
from lapa_ng.rules_regex import (
    RegexRuleSpec,
)
from lapa_ng.types import Matcher, MatchResult, Phoneme, Word


def RegexMatcher(id: str, rule: str, replacement: str):
    """
    Just a factory function to create a RegexMatcher from individual arguments.
    """
    replacement = [Phoneme(sampa=p) for p in replacement.split(" ") if p]
    spec = RegexRuleSpec(id=id, pattern=rule, replacement=replacement)
    return _RegexMatcher(spec)


def test_find_candidate_rules():
    rules = (
        RegexMatcher(id="r1", rule="^(ab)", replacement="P A"),
        RegexMatcher(id="r2", rule="(ab)a", replacement="X1"),
        RegexMatcher(id="r3", rule="(ab)b", replacement="AB"),
        RegexMatcher(id="r4", rule="(ba)", replacement="PC"),
    )

    matcher = RegexListMatcher(rules)

    result = matcher.find_candidate_rules(word=Word("a"), start=0)
    assert [r.id for r in result] == ["r1", "r2", "r3"]

    result = matcher.find_candidate_rules(word=Word("xa"), start=1)
    assert [r.id for r in result] == ["r2", "r3"]

    result = matcher.find_candidate_rules(word=Word("xxxb"), start=3)
    assert [r.id for r in result] == ["r4"]


def test_find_cached_rules():
    rules = (
        RegexMatcher(id="r1", rule="^(ab)", replacement="P A"),
        RegexMatcher(id="r2", rule="(ab)a", replacement="X1"),
        RegexMatcher(id="r3", rule="(ab)b", replacement="AB"),
        RegexMatcher(id="r4", rule="(ba)", replacement="PC"),
    )

    matcher = RegexListMatcher(rules)
    assert len(matcher.candidate_cache) == 0

    result = matcher.find_candidate_rules(word=Word("a"), start=0)
    assert [r.id for r in result] == ["r1", "r2", "r3"]

    # Poison the cache
    key = list(matcher.candidate_cache.keys())[0]
    matcher.candidate_cache[key] = "MY CRAZY CACHE OBJECT"

    result = matcher.find_candidate_rules(word=Word("a"), start=0)
    assert result == "MY CRAZY CACHE OBJECT"


def test_match():
    class MockMatcher(Matcher):
        id = "MockMatcher"

        def __init__(self, word: str):
            self.word = word

        def match(self, word, start):
            if word.text == self.word:
                yield MatchResult(word, [Phoneme(sampa="P")], 0, "P", "A")

    rules = [MockMatcher(word="a"), MockMatcher(word="b")]

    matcher = RegexListMatcher(rules)
    matcher.find_candidate_rules = lambda *args, **kwargs: rules

    result = list(matcher.match(word=Word("a"), start=0))
    assert len(result) == 1
    assert result[0].phonemes == [Phoneme(sampa="P")]
    assert len(result[0].rules_attempted) == 0

    result = list(matcher.match(word=Word("b"), start=0))
    assert len(result) == 1
    assert result[0].phonemes == [Phoneme(sampa="P")]
    assert len(result[0].rules_attempted) == 1
