"""
Command-line interface for the LAPA-NG package.

This module provides various commands for testing, converting, and processing
rules and text using the LAPA-NG phonetic transcription system.
"""

import json
from typing import List

import click
import yaml


@click.group()
def cli():
    """LAPA-NG command-line interface for phonetic transcription and rule processing."""
    pass


@cli.command()
@click.argument("rule_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--sheet", type=str)
def convert_excel(rule_file: str, output_file: str, sheet: str | None):
    """Convert Excel rules file to YAML format.

    Args:
        input_file: Path to input Excel file
        output_file: Path to output YAML file
        sheet: Optional sheet name to convert
    """
    from lapa_ng.table_rules import load_matcher

    matcher = load_matcher(rule_file, sheet_name=sheet)
    rules = [r.spec.asdict() for r in matcher.rules]

    with open(output_file, "w") as f:
        if ".json" in output_file:
            json.dump(rules, f, indent=4)
        else:
            yaml.dump(rules, f, sort_keys=False, default_flow_style=False)


@cli.command()
@click.argument("naf_file", type=click.Path(exists=True))
@click.argument("rule_file", type=click.Path(exists=True))
@click.option("--sheet", type=str, default=None)
def translate_naf(naf_file: str, rule_file: str, sheet: str):
    """Translate text from a NAF file using specified rules.

    Args:
        naf_file: Path to input NAF file
        rule_file: Path to rules file
        worksheet: Optional worksheet name to use
    """
    import csv

    from lapa_ng.naf import parse_naf
    from lapa_ng.table_rules import load_matcher
    from lapa_ng.text_clean import clean_words, default_cleaners
    from lapa_ng.translator import CachedTranslator, MatchingTranslator

    matcher = load_matcher(rule_file, sheet_name=sheet)
    translator = MatchingTranslator(matcher)
    translator = CachedTranslator(translator)

    input = parse_naf(naf_file)
    input = clean_words(input, default_cleaners)
    output = translator.translate(input, emit="phoneme")

    with open("output.csv", "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, delimiter=",")
        writer.writerow(
            [
                "id",
                "text",
                "start",
                "matched",
                "phoneme",
                "rule_id",
                "rules_attempted",
            ]
        )

        for result in output:
            attribs = result.word.attributes
            text = result.word.text
            word_id = attribs.get("id", "")
            ruled_id = result.match_results[0].rule_id
            rules_attempted = len(result.match_results[0].rules_attempted)

            for ph_ix, ph in enumerate(result.phonemes):
                writer.writerow(
                    [
                        word_id,
                        text,
                        ph_ix,
                        ph.sampa,
                        ruled_id,
                        rules_attempted,
                    ]
                )


@cli.command()
@click.argument("rule_file", type=click.Path(exists=True))
@click.argument("words", type=str, nargs=-1)
@click.option("--sheet", type=str, default=None)
def translate_words(words: List[str], rule_file: str, sheet: str):
    """Test word transcription using specified rules and engine.

    Args:
        words: One or more words to transcribe
        rule_file: Path to the rules file
        engine: Transcription engine to use ('sampify' or 'lapa')
    """
    from lapa_ng.table_rules import load_matcher
    from lapa_ng.text_clean import clean_words, default_cleaners
    from lapa_ng.translator import CachedTranslator, MatchingTranslator
    from lapa_ng.types import Word

    matcher = load_matcher(rule_file, sheet_name=sheet)
    translator = MatchingTranslator(matcher)
    translator = CachedTranslator(translator)

    input = [Word(text=w, attributes={"id": str(ix)}) for ix, w in enumerate(words)]
    input = clean_words(input, default_cleaners)
    output = translator.translate(input, emit="word")

    for result in output:
        print(result.word.text, " ".join([ph.sampa for ph in result.phonemes]))


@cli.command()
def test():
    """Test word transcription using specified rules and engine."""
    import csv

    from lapa_ng.classic import ClassicMatcher
    from lapa_ng.naf import parse_naf
    from lapa_ng.table_rules import load_matcher
    from lapa_ng.text_clean import clean_words, default_cleaners
    from lapa_ng.translator import CachedTranslator, MatchingTranslator

    matcher = ClassicMatcher("fixtures/RULES_A_V1.5.xls", sheet_name="RULES")
    translator = MatchingTranslator(matcher)
    translator = CachedTranslator(translator)

    input = parse_naf("fixtures/vond001gysb04_01.xml")
    input = clean_words(input, default_cleaners)
    output = translator.translate(input, emit="phoneme")

    with open("output.csv", "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, delimiter=",")
        writer.writerow(
            [
                "id",
                "text",
                "start",
                "matched",
                "phoneme",
                "rule_id",
                "rules_attempted",
            ]
        )

        for result in output:
            attribs = result.word.attributes
            text = result.word.text
            word_id = attribs.get("id", "")
            rule_id = result.match_results[0].rule_id
            rules_attempted = len(result.match_results[0].rules_attempted)

            for ph_ix, ph in enumerate(result.phonemes):
                writer.writerow(
                    [
                        word_id,
                        text,
                        ph_ix,
                        ph.sampa,
                        rule_id,
                        rules_attempted,
                    ]
                )
