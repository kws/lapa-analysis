from typing import Generator, Iterable

from cachetools import LFUCache

from lapa_ng.types import (
    EmitValue,
    Matcher,
    MatchResult,
    TranslationResult,
    Translator,
    Word,
    WordOrWordList,
)


def _collect_words(
    result: Iterable[TranslationResult],
) -> Generator[TranslationResult, None, None]:
    """Coalesce TranslationResult into a list of TranslationResult for each word.

    This function takes a sequence of translation results and groups them by word,
    combining the phonemes and match results for each word into a single result.

    Args:
        result: An iterable of TranslationResult objects

    Yields:
        TranslationResult objects grouped by word
    """

    def yield_word_result(
        word: Word, translations: list[TranslationResult]
    ) -> Generator[TranslationResult, None, None]:
        """Yield a single TranslationResult for a word from multiple results.

        Args:
            word: The word being translated
            translations: List of translation results for this word

        Yields:
            A single TranslationResult combining all phonemes and match results
        """
        phonemes = [ph for t in translations for ph in t.phonemes]
        match_results = [mr for t in translations for mr in t.match_results]
        yield TranslationResult(
            word=word, phonemes=phonemes, match_results=match_results
        )

    current_word: Word | None = None
    current_translations: list[TranslationResult] = []

    for r in result:
        if r.word != current_word:
            if current_word:
                yield from yield_word_result(current_word, current_translations)
            current_word = r.word
            current_translations = []

        current_translations.append(r)

    if current_word:
        yield from yield_word_result(current_word, current_translations)


def _collect_rules(
    result: Iterable[TranslationResult],
) -> Generator[TranslationResult, None, None]:
    """Pass through translation results without modification.

    This function serves as an identity function for translation results,
    yielding them unchanged. It's used when the 'rule' emit value is specified.

    Args:
        result: An iterable of TranslationResult objects

    Yields:
        The same TranslationResult objects as input
    """
    yield from result


def _collect_phonemes(
    result: Iterable[TranslationResult],
) -> Generator[TranslationResult, None, None]:
    """Split translation results into individual phonemes.

    This function takes translation results and yields a separate result
    for each phoneme, maintaining the word and match result information.

    Args:
        result: An iterable of TranslationResult objects

    Yields:
        TranslationResult objects, one for each phoneme
    """
    for r in result:
        for phoneme in r.phonemes:
            yield TranslationResult(
                word=r.word, phonemes=[phoneme], match_results=r.match_results
            )


class MatchingTranslator(Translator):
    """A translator that uses a matcher to translate words into phonemes.

    This class implements the Translator protocol by using a Matcher to find
    matches between words and rules, producing phonetic transcriptions.

    Attributes:
        matcher: The matcher used to find matches between words and rules
    """

    def __init__(self, matcher: Matcher):
        """Initialize the translator with a matcher.

        Args:
            matcher: The matcher to use for finding matches
        """
        self.matcher = matcher

    def translate(
        self, word: WordOrWordList, *, emit: EmitValue = "rule"
    ) -> Generator[TranslationResult, None, None]:
        """Translate words into phonemes using the given matcher.

        This function attempts to match the entire word against the rules and yields
        a TranslationResult for each match found. If no rule matches a character,
        it yields a 'silent' match with empty phonemes.

        Args:
            word: The word or words to translate
            emit: The granularity at which to emit results (word, rule, or phoneme)

        Yields:
            TranslationResult objects for each match or non-match in the word
        """
        assert emit in ("word", "rule", "phoneme")

        if emit == "rule":
            collector = _collect_rules
        elif emit == "word":
            collector = _collect_words
        else:
            collector = _collect_phonemes

        if isinstance(word, Word):
            word = [word]

        for w in word:
            yield from collector(self._translate_word(w))

    def _translate_word(self, word: Word) -> Generator[TranslationResult, None, None]:
        """Translate a single word into phonemes.

        This internal method handles the actual translation of a word by
        repeatedly matching substrings against rules until the entire word
        is processed.

        Args:
            word: The word to translate

        Yields:
            TranslationResult objects for each match in the word
        """
        word_remainder = word.text
        start_length = len(word_remainder)

        while word_remainder:
            current_length = len(word_remainder)
            current_pos = start_length - current_length

            matched: list[MatchResult] = list(
                self.matcher.match(word=word, start=current_pos)
            )
            if matched:
                word_remainder = matched[-1].remainder
            else:
                # If no match, yield a 'silent' match with empty phonemes
                matched_part = word_remainder[0]
                word_remainder = word_remainder[1:]
                matched.append(
                    MatchResult(
                        word=word,
                        phonemes=[],
                        start=current_pos,
                        matched=matched_part,
                        remainder=word_remainder,
                    )
                )

            for match_result in matched:
                yield TranslationResult(
                    word=match_result.word,
                    phonemes=match_result.phonemes,
                    match_results=[match_result],
                )


class CachedTranslator(Translator):
    """A translator that caches results to improve performance.

    This class wraps a translator and caches its results to avoid
    recomputing translations for the same words. It uses an LFU (Least
    Frequently Used) cache to manage the cache size.

    Attributes:
        cache: The LFU cache storing translation results
        parent: The underlying translator being cached
    """

    def __init__(self, parent: Translator, cache_size: int = 10_000):
        """Initialize with a translator and cache size.

        Args:
            parent: The translator to cache results from
            cache_size: Maximum number of translations to cache
        """
        self.cache = LFUCache(maxsize=cache_size)
        self.parent = parent

    def translate(
        self, word: WordOrWordList, *, emit: EmitValue | None = None
    ) -> Generator[TranslationResult, None, None]:
        """Translate words using the cached translator.

        This method first checks the cache for existing translations.
        If found, it yields the cached results. Otherwise, it computes
        the translation using the parent translator and caches the results.

        Args:
            word: The word or words to translate
            emit: The granularity at which to emit results

        Yields:
            TranslationResult objects containing the phonetic translations
        """
        word = [word] if isinstance(word, Word) else word
        for w in word:
            value = self.cache.get((w.text, emit))
            if value:
                yield from value
                continue

            t = tuple(self.parent.translate(w, emit=emit))
            self.cache[(w.text, emit)] = t
            yield from t
