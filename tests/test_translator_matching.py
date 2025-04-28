from unittest.mock import Mock, patch

import pytest

from lapa_ng.translator import MatchingTranslator
from lapa_ng.types import MatchResult, Word


@patch("lapa_ng.translator.MatchingTranslator._translate_word")
@patch("lapa_ng.translator._collect_words")
@patch("lapa_ng.translator._collect_rules")
@patch("lapa_ng.translator._collect_phonemes")
def test_emit_settings(
    mock_collect_phonemes, mock_collect_rules, mock_collect_words, mock_translate_word
):
    # Setup mock return values
    mock_translate_word.return_value = "My Translation Result"
    mock_collect_words.return_value = []
    mock_collect_rules.return_value = []
    mock_collect_phonemes.return_value = []

    translator = MatchingTranslator(None)
    list(translator.translate(Word(text="test")))
    mock_collect_rules.assert_called_once()
    mock_collect_words.assert_not_called()
    mock_collect_phonemes.assert_not_called()
    assert mock_collect_rules.call_args[0][0] == "My Translation Result"

    mock_translate_word.reset_mock()
    mock_collect_rules.reset_mock()
    mock_collect_phonemes.reset_mock()

    list(translator.translate(Word(text="test"), emit="word"))
    mock_translate_word.assert_called_once()
    mock_translate_word.reset_mock()

    list(translator.translate(Word(text="test"), emit="rule"))
    mock_collect_rules.assert_called_once()
    mock_collect_rules.reset_mock()

    list(translator.translate(Word(text="test"), emit="phoneme"))
    mock_collect_phonemes.assert_called_once()
    mock_collect_phonemes.reset_mock()

    with pytest.raises(AssertionError):
        list(translator.translate(Word(text="test"), emit="invalid"))


def test_translate_word_matches():
    mock_matcher = Mock()
    mock_matcher.match.return_value = [
        MatchResult(
            phonemes=["t", "e"],
            word=Word(text="test"),
            start=0,
            matched="te",
            remainder="st",
        ),
        MatchResult(
            phonemes=["s", "t"],
            word=Word(text="test"),
            start=2,
            matched="st",
            remainder="",
        ),
    ]

    translator = MatchingTranslator(mock_matcher)
    result = list(translator._translate_word(Word(text="test")))
    assert len(result) == 2
    assert result[0].phonemes == ["t", "e"]
    assert result[1].phonemes == ["s", "t"]


def test_translate_word_no_matches():
    mock_matcher = Mock()
    mock_matcher.match.return_value = []
    translator = MatchingTranslator(mock_matcher)
    result = list(translator._translate_word(Word(text="test")))
    assert len(result) == 4
    assert result[0].phonemes == []
    assert result[1].phonemes == []
    assert result[2].phonemes == []
    assert result[3].phonemes == []
