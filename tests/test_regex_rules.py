from lapa_ng.rules_regex import RegexMatcher, RegexRuleSpec
from lapa_ng.types import Phoneme, Word


def test_prefix_matcher_start():
    phA = Phoneme(sampa="A")

    spec = RegexRuleSpec(id="test", pattern="^(a)", replacement=[phA])
    matcher = RegexMatcher(spec)

    result_list = matcher.match(word=Word("aan"), start=0)
    result_list = list(result_list)

    assert len(result_list) == 1
    result = result_list[0]

    assert result
    assert result.matched == "a"
    assert result.phonemes == (phA,)
    assert result.word.text == "aan"
    assert result.remainder == "an"


def test_prefix_matcher_not_start():
    phA = Phoneme(sampa="A")

    spec = RegexRuleSpec(id="test", pattern="^(a)", replacement=[phA])
    matcher = RegexMatcher(spec)

    result_list = matcher.match(word=Word("aan"), start=1)
    result_list = list(result_list)

    assert len(result_list) == 0


def test_non_prefix_matcher():
    phA = Phoneme(sampa="A")
    phB = Phoneme(sampa="B")

    spec = RegexRuleSpec(id="test", pattern="(ab)ba", replacement=[phA, phB])
    matcher = RegexMatcher(spec)

    result_list = matcher.match(word=Word("abbabbabdo"), start=0)
    result_list = list(result_list)

    assert len(result_list) == 1
    result = result_list[0]

    assert result
    assert result.matched == "ab"
    assert result.phonemes == (phA, phB)
    assert result.word.text == "abbabbabdo"
    assert result.remainder == "babbabdo"


def test_non_prefix_matcher_no_match():
    phA = Phoneme(sampa="A")
    phB = Phoneme(sampa="B")

    spec = RegexRuleSpec(id="test", pattern="(ab)ba", replacement=[phA, phB])
    matcher = RegexMatcher(spec)

    result_list = matcher.match(word=Word("abbabbabdo"), start=2)
    result_list = list(result_list)

    assert len(result_list) == 0


def test_non_prefix_matcher_matched_in_middle():
    phA = Phoneme(sampa="A")
    phB = Phoneme(sampa="B")

    spec = RegexRuleSpec(id="test", pattern="(ab)ba", replacement=[phA, phB])
    matcher = RegexMatcher(spec)

    result_list = matcher.match(word=Word("abbabbabdo"), start=3)
    result_list = list(result_list)

    assert len(result_list) == 1
    result = result_list[0]

    assert result
    assert result.matched == "ab"
    assert result.phonemes == (phA, phB)
    assert result.start == 3
    assert result.word.text == "abbabbabdo"
    assert result.remainder == "babdo"
