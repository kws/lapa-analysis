from unittest.mock import Mock

from lapa_ng.translator import CachedTranslator
from lapa_ng.types import MatchResult, TranslationResult, Word


def test_cached_translator():
    word = Word(text="test")

    mock_translator = Mock()
    mock_translator.translate.return_value = [
        TranslationResult(word=word, phonemes=["t", "e"], match_results=[]),
        TranslationResult(word=word, phonemes=["s", "t"], match_results=[]),
    ]

    translator = CachedTranslator(mock_translator)

    result = list(translator.translate(word))
    assert len(result) == 2
    assert mock_translator.translate.call_count == 1
    mock_translator.translate.reset_mock()

    result = list(translator.translate(word))
    assert len(result) == 2
    assert mock_translator.translate.call_count == 0
    mock_translator.translate.reset_mock()

    result = list(translator.translate(Word(text="test", attributes=dict(id="55"))))
    assert len(result) == 2
    assert mock_translator.translate.call_count == 0
    mock_translator.translate.reset_mock()

    result = list(translator.translate(word, emit="phoneme"))
    assert len(result) == 2
    assert mock_translator.translate.call_count == 1
    mock_translator.translate.reset_mock()

    result = list(translator.translate(word, emit="phoneme"))
    assert len(result) == 2
    assert mock_translator.translate.call_count == 0
    mock_translator.translate.reset_mock()
