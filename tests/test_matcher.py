from lapa_ng.rules.matchers import RuleListMatcher, translate
from lapa_ng.rules_regex.rules import RegexMatcher

def test_prefix_matcher_start():
    matcher = RegexMatcher(id = "test", rule = "^(a)", replacement = "A")

    result = matcher.match(word = "aan", start = 0)
    assert result
    assert result.matched == "a"
    assert result.phonemes == "A"
    assert result.word == "aan"
    assert result.remainder == "an"

def test_prefix_matcher_not_start():
    matcher = RegexMatcher(id = "test", rule = "^(a)", replacement = "A")

    result = matcher.match(word = "aan", start = 1)
    assert result is None

def test_non_prefix_matcher():
    matcher = RegexMatcher(id = "test", rule = "(ab)ba", replacement = "A B")

    result = matcher.match(word = "abbabbabdo", start = 0)
    assert result
    assert result.matched == "ab"
    assert result.phonemes == "A B"
    assert result.word == "abbabbabdo"
    assert result.remainder == "babbabdo"

def test_non_prefix_matcher_no_match():
    matcher = RegexMatcher(id = "test", rule = "(ab)ba", replacement = "A B")

    result = matcher.match(word = "abbabbabdo", start = 2)
    assert result is None

def test_non_prefix_matcher_matched_in_middle():
    matcher = RegexMatcher(id = "test", rule = "(ab)ba", replacement = "A B")

    result = matcher.match(word = "abbabbabdo", start = 3)
    assert result
    assert result.matched == "ab"
    assert result.phonemes == "A B"
    assert result.start == 3
    assert result.word == "abbabbabdo"
    assert result.remainder == "babdo"


def test_match_word():
    rules = (
        RegexMatcher(id = "r1", rule = "^(ab)", replacement = "P A"),
        RegexMatcher(id = "r2", rule = "(ab)a", replacement = "X1"),
        RegexMatcher(id = "r3", rule = "(ab)b", replacement = "AB"),
        RegexMatcher(id = "r4", rule = "(ba)", replacement = "PC"),
    )

    matcher = RuleListMatcher(rules)

    result = list(translate(word = "abbabbaabba", part_matcher = matcher))
    assert len(result) == 6

    matched_rules_ids = [r.rule_id for r in result]
    assert matched_rules_ids == ["r1", "r4", "NO_MATCH", 'r4', 'r3', 'r4']

    phonemes = " ".join([r.match_result.phonemes for r in result if r.match_result.phonemes])
    reconstructed_word = "".join([r.match_result.matched for r in result if r.match_result.matched])
    assert phonemes == "P A PC PC AB PC"
    assert reconstructed_word == "abbabbaabba"
