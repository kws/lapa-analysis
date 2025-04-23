from logging import getLogger
from typing import Generator, Iterable, NamedTuple
from lapa_ng.naf import WordForm, parse_naf
from lapa_ng.pipeline.clean import ensure_text
from lapa_ng.rules.matchers import CachedTranslator, ContextualMatchResult, Matcher, translate as default_translate
from lapa_ng.rules_regex.matching import RegexListMatcher
from lapa_ng.rules_regex.rules import RegexMatcher
from lapa_ng.rules_table.regex import rule_to_regex
from lapa_ng.rules_table.table import check_rules_for_duplicate_priorities, read_excel, sort_rules_by_numeric_priority


logger = getLogger(__name__)

__all__ = ["load_matchers_from_excel", "translate_naf"]

class TranslationResult(NamedTuple):
    word_index: int
    word_form: WordForm
    translation_index: int
    translation: ContextualMatchResult

class TranslatedWordResult(NamedTuple):
    word_index: int
    word_form: WordForm
    phonemes: str
    translation: list[ContextualMatchResult]

class TranslatedPhonemeResult(NamedTuple):
    phoneme: str
    phoneme_index: int  
    translation: TranslationResult


def translate_naf(naf_file: str, matcher: Matcher, *, preprocessor: callable = None, translator: callable = None) -> Generator[TranslationResult, None, None]:
    """
    Translate a NAF file using a translator.
    """
    if preprocessor is None:
        preprocessor = ensure_text
    if translator is None:
        translator = CachedTranslator(default_translate)

    for word_ix, text in enumerate(parse_naf(naf_file)):
        cleaned_text = preprocessor(text.text)
        for t_ix, t in enumerate(translator(cleaned_text, matcher)):
            yield TranslationResult(word_ix, text, t_ix, t)

def coalesce_translations(translations: Iterable[TranslationResult], *, filter_silent: bool = True) -> Generator[TranslatedWordResult, None, None]:
    """
    Coalesce translations into a list of TranslatedWordResult.
    """
    def yield_word_result(word_index: int, word: WordForm, translations: list[ContextualMatchResult]) -> Generator[TranslatedWordResult, None, None]:
        if word:
            phonemes = ' '.join(t.translation.match_result.phonemes for t in translations if t.translation.match_result.phonemes).strip()
            if filter_silent and phonemes == "":
                return
            yield TranslatedWordResult(word_index, word, phonemes, translations)

    current_word_index: int | None = None
    current_word: WordForm | None = None
    current_translations: list[ContextualMatchResult] = []
    
    for t in translations:
        if t.word_index != current_word_index:
            yield from yield_word_result(current_word_index, current_word, current_translations)
            current_word_index = t.word_index
            current_word = t.word_form
            current_translations = []

        current_translations.append(t)

    yield from yield_word_result(current_word_index, current_word, current_translations)

def explode_translations(translations: Iterable[TranslationResult], *, filter_silent: bool = True) -> Generator[TranslatedPhonemeResult, None, None]:
    for t in translations:
        for i, ph in enumerate(t.translation.match_result.phonemes.split(" ")):
            if filter_silent and ph == "":
                continue
            yield TranslatedPhonemeResult(ph, i, t)
