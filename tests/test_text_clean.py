from unittest.mock import Mock, call

from lapa_ng.text_clean import (
    clean_words,
    create_pipeline,
    ensure_text,
    strip_accents,
    strip_spaces,
    to_lowercase,
)
from lapa_ng.types import Word


def test_ensure_text():
    assert ensure_text("hello") == "hello"
    assert ensure_text(None) == ""
    assert ensure_text(123) == "123"


def test_strip_spaces():
    assert strip_spaces("hello") == "hello"
    assert strip_spaces(" hello ") == "hello"
    assert strip_spaces("hello ") == "hello"
    assert strip_spaces(" hello") == "hello"
    assert strip_spaces("") == ""


def test_to_lowercase():
    assert to_lowercase("Hello") == "hello"
    assert to_lowercase("HELLO") == "hello"
    assert to_lowercase("hello") == "hello"

    # Dutch ij digraph using regular ASCII letters
    assert to_lowercase("IJsselmeer") == "ijsselmeer"
    assert to_lowercase("IJSSELMEER") == "ijsselmeer"

    # Dutch ij ligature (rare in modern use)
    assert to_lowercase("Ĳsselmeer") == "ĳsselmeer"
    assert to_lowercase("ĲĲ") == "ĳĳ"

    # Accented letters, relevant in borrowed Dutch words
    assert to_lowercase("ÉÉN") == "één"
    assert to_lowercase("GÉÉN") == "géén"
    assert to_lowercase("Über") == "über"

    # Other Latin extended characters
    assert to_lowercase("Ç") == "ç"
    assert to_lowercase("ÅNGST") == "ångst"


def test_strip_accents():
    assert strip_accents("héllo") == "hello"

    # Common accented vowels
    assert strip_accents("àèìòù") == "aeiou"
    assert strip_accents("áéíóú") == "aeiou"
    assert strip_accents("âêîôû") == "aeiou"
    assert strip_accents("äëïöü") == "aeiou"
    assert strip_accents("ãẽĩõũ") == "aeiou"

    # Accented uppercase
    assert strip_accents("ÀÈÌÒÙ") == "AEIOU"
    assert strip_accents("ÁÉÍÓÚ") == "AEIOU"
    assert strip_accents("ÂÊÎÔÛ") == "AEIOU"
    assert strip_accents("ÄËÏÖÜ") == "AEIOU"

    # Dutch examples
    assert strip_accents("één") == "een"
    assert strip_accents("GÉÉN") == "GEEN"

    # Characters with cedilla and ring
    assert strip_accents("ç") == "c"
    assert strip_accents("Ç") == "C"
    assert strip_accents("Å") == "A"
    assert strip_accents("å") == "a"


def test_create_pipeline():
    func1 = Mock()
    func2 = Mock()

    pipeline = create_pipeline(func1, func2)
    pipeline("A")
    func1.assert_called_once_with("A")
    func2.assert_called_once_with(func1.return_value)

    func1.reset_mock()
    func2.reset_mock()

    pipeline("B")
    func1.assert_called_once_with("B")
    func2.assert_called_once_with(func1.return_value)


def test_clean_words():
    func1 = Mock()
    func1.side_effect = ["f1r1", "f1r2"]
    func2 = Mock()
    func2.side_effect = ["f2r1", "f2r2"]

    words = [Word(text="hello"), Word(text="world")]
    result = list(clean_words(words, func1, func2))

    func1.assert_has_calls([call("hello"), call("world")])
    func2.assert_has_calls([call("f1r1"), call("f1r2")])

    assert len(result) == 2

    assert result[0].text == "f2r1"
    assert result[0].attributes == {"original_text": "hello"}

    assert result[1].text == "f2r2"
    assert result[1].attributes == {"original_text": "world"}


def test_clean_words_no_changes():
    func1 = lambda x: x
    func2 = lambda x: x

    words = [Word(text="hello"), Word(text="world")]
    result = list(clean_words(words, func1, func2))

    assert len(result) == 2

    assert result[0].text == "hello"
    assert "original_text" not in result[0].attributes

    assert result[1].text == "world"
    assert "original_text" not in result[1].attributes
