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

def load_matchers_from_excel(rules_file: str, sheet_name: str | int | None = None, sort_function: callable = sort_rules_by_numeric_priority) -> Matcher:
    """
    Create a translator from a rules file.
    """
    rules = read_excel(rules_file, sheet_name = sheet_name)

    duplicates = check_rules_for_duplicate_priorities(rules)
    for k, v in duplicates.items():
        logger.warning(f"For letter {k[0]} and priority {k[3]} there are {len(v)} duplicates: {', '.join(r.rule_id for r in v)}")

    regex_list = []
    for r in sort_function(rules):
        try:
            regex_list.append(rule_to_regex(r)) 
        except Exception as e:
            print(e)
    
    regex_matchers = [RegexMatcher(r.id, r.pattern, r.replacement, r.meta) for r in regex_list]
    matcher_list = RegexListMatcher(regex_matchers)
    return matcher_list


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

def coalesce_translations(translations: Iterable[TranslationResult]) -> Generator[TranslatedWordResult, None, None]:
    """
    Coalesce translations into a list of TranslatedWordResult.
    """
    current_word_index: int | None = None
    current_word: WordForm | None = None
    current_translations: list[ContextualMatchResult] = []
    for t in translations:
        if t.word_index != current_word_index:
            if current_word:
                phonemes = ' '.join(ct.translation.match_result.phonemes for ct in current_translations if ct.translation.match_result.phonemes).strip()
                yield TranslatedWordResult(t.word_index, current_word, phonemes, current_translations)
            current_word_index = t.word_index
            current_word = t.word_form
            current_translations = []

        current_translations.append(t)

    if current_word:
        phonemes = ' '.join(t.translation.match_result.phonemes for t in current_translations if t.translation.match_result.phonemes)
        yield TranslatedWordResult(t.word_index, current_word, phonemes, current_translations)

