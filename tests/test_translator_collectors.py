from lapa_ng.translator import (
    CachedTranslator,
    MatchingTranslator,
    _collect_phonemes,
    _collect_rules,
    _collect_words,
)
from lapa_ng.types import MatchResult, TranslationResult, Word


def test_collect_words_single_word():
    # Test case 1: Single word with multiple translations
    word1 = Word(text="test")
    results1 = [
        TranslationResult(
            word=word1,
            phonemes=["t"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["t"], start=0, matched="t", remainder="est"
                )
            ],
        ),
        TranslationResult(
            word=word1,
            phonemes=["e"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["e"], start=1, matched="e", remainder="st"
                )
            ],
        ),
        TranslationResult(
            word=word1,
            phonemes=["s", "t"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["s", "t"], start=2, matched="st", remainder=""
                )
            ],
        ),
    ]

    collected1 = list(_collect_words(results1))
    assert len(collected1) == 1
    assert collected1[0].word == word1
    assert collected1[0].phonemes == ["t", "e", "s", "t"]
    assert len(collected1[0].match_results) == 3


def test_collect_words_multiple_words():
    # Test case 2: Multiple words
    word1 = Word(text="test")
    word2 = Word(text="hello")
    results2 = [
        TranslationResult(
            word=word1,
            phonemes=["t", "e"],
            match_results=[
                MatchResult(
                    word=word1,
                    phonemes=["t", "e"],
                    start=0,
                    matched="test",
                    remainder="st",
                )
            ],
        ),
        TranslationResult(
            word=word1,
            phonemes=["s", "t"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["s", "t"], start=2, matched="st", remainder=""
                )
            ],
        ),
        TranslationResult(
            word=word2,
            phonemes=["h", "e", "l", "l"],
            match_results=[
                MatchResult(
                    word=word2,
                    phonemes=["h", "e", "l", "l"],
                    start=0,
                    matched="hello",
                    remainder="o",
                )
            ],
        ),
        TranslationResult(
            word=word2,
            phonemes=["o"],
            match_results=[
                MatchResult(
                    word=word2, phonemes=["o"], start=4, matched="o", remainder=""
                )
            ],
        ),
    ]

    collected2 = list(_collect_words(results2))
    assert len(collected2) == 2
    assert collected2[0].word == word1
    assert collected2[0].phonemes == ["t", "e", "s", "t"]
    assert collected2[1].word == word2
    assert collected2[1].phonemes == ["h", "e", "l", "l", "o"]


def test_collect_words_empty_input():
    # Test case 3: Empty input
    collected3 = list(_collect_words([]))
    assert len(collected3) == 0


def test_collect_words_single_word_no_phonemes():
    # Test case 4: Single word with no phonemes
    word3 = Word(text="empty")
    results4 = [
        TranslationResult(
            word=word3,
            phonemes=[],
            match_results=[
                MatchResult(
                    word=word3, phonemes=[], start=0, matched="", remainder="empty"
                )
            ],
        )
    ]

    collected4 = list(_collect_words(results4))
    assert len(collected4) == 1
    assert collected4[0].word == word3
    assert collected4[0].phonemes == []
    assert len(collected4[0].match_results) == 1


def test_collect_rules():
    word1 = Word(text="test")
    results1 = [
        TranslationResult(
            word=word1,
            phonemes=["t"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["t"], start=0, matched="t", remainder="est"
                )
            ],
        ),
        TranslationResult(
            word=word1,
            phonemes=["e"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["e"], start=1, matched="e", remainder="st"
                )
            ],
        ),
        TranslationResult(
            word=word1,
            phonemes=["s", "t"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["s", "t"], start=2, matched="st", remainder=""
                )
            ],
        ),
    ]
    collected1 = list(_collect_rules(results1))

    assert len(collected1) == 3
    assert collected1[0].word == word1
    assert collected1[0].phonemes == ["t"]
    assert collected1[1].word == word1
    assert collected1[1].phonemes == ["e"]
    assert collected1[2].word == word1
    assert collected1[2].phonemes == ["s", "t"]


def test_collect_phonemes():
    word1 = Word(text="test")
    word2 = Word(text="hello")
    results1 = [
        TranslationResult(
            word=word1,
            phonemes=["t"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["t"], start=0, matched="t", remainder="est"
                )
            ],
        ),
        TranslationResult(
            word=word1,
            phonemes=["e"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["e"], start=1, matched="e", remainder="st"
                )
            ],
        ),
        TranslationResult(
            word=word1,
            phonemes=["s", "t"],
            match_results=[
                MatchResult(
                    word=word1, phonemes=["s", "t"], start=2, matched="st", remainder=""
                )
            ],
        ),
        TranslationResult(
            word=word2,
            phonemes=["h", "e", "l", "l"],
            match_results=[
                MatchResult(
                    word=word2,
                    phonemes=["h", "e", "l", "l"],
                    start=0,
                    matched="hello",
                    remainder="o",
                )
            ],
        ),
        TranslationResult(
            word=word2,
            phonemes=["o"],
            match_results=[
                MatchResult(
                    word=word2, phonemes=["o"], start=4, matched="o", remainder=""
                )
            ],
        ),
    ]

    collected1 = list(_collect_phonemes(results1))
    assert len(collected1) == 9
    assert collected1[0].word == word1
    assert collected1[-1].word == word2

    assert collected1[0].phonemes == ["t"]
    assert collected1[1].phonemes == ["e"]
    assert collected1[2].phonemes == ["s"]
    assert collected1[3].phonemes == ["t"]
    assert collected1[4].phonemes == ["h"]
    assert collected1[5].phonemes == ["e"]
    assert collected1[6].phonemes == ["l"]
    assert collected1[7].phonemes == ["l"]
    assert collected1[8].phonemes == ["o"]
