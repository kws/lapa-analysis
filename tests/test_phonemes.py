import pytest

from lapa_ng.phonemes import PhonemeList
from lapa_ng.types import Phoneme


def test_phoneme_list():
    phonemes = PhonemeList.default()
    assert len(phonemes) == 43

    assert phonemes[0].sampa == "a:"
    assert phonemes[0].ipa == "/aː/"


def test_phoneme_extractor():

    result = PhonemeList.default().split_phonemes("9ytg#zOnd#rt")
    phonemes = [phoneme.sampa for phoneme in result]

    assert phonemes == ["9y", "t", "g", "#", "z", "O", "n", "d", "#", "r", "t"]


def test_split_phonemes_ignore_errors():
    result = PhonemeList.default().split_phonemes("t-t", ignore_errors=True)
    phonemes = [phoneme.sampa for phoneme in result]
    assert phonemes == ["t", "t"]


def test_split_phonemes_raise_errors():
    with pytest.raises(ValueError):
        PhonemeList.default().split_phonemes("t-t")


def test_phoneme_list():
    phonemes = PhonemeList(
        [
            Phoneme(sampa="a"),
            Phoneme(sampa="b"),
            Phoneme(sampa="c"),
        ]
    )

    assert len(phonemes) == 3
    assert len(list(phonemes)) == 3
    assert phonemes[0].sampa == "a"
    assert phonemes["a"].sampa == "a"

    with pytest.raises(IndexError):
        phonemes[5]

    with pytest.raises(KeyError):
        phonemes["d"]
