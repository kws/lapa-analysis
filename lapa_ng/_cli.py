"""
Command-line interface for the LAPA-NG package.

This module provides various commands for testing, converting, and processing
rules and text using the LAPA-NG phonetic transcription system.
"""

import csv
import json
from typing import List

import click
import yaml

from lapa_ng.factory import create_matcher
from lapa_ng.naf import parse_naf
from lapa_ng.table_rules import load_regex_matcher_list
from lapa_ng.text_clean import clean_words, default_cleaners
from lapa_ng.translator import CachedTranslator, MatchingTranslator
from lapa_ng.types import Word


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
    matcher_list = load_regex_matcher_list(rule_file, sheet_name=sheet)
    rules = [r.spec.asdict() for r in matcher_list]

    with open(output_file, "w") as f:
        if ".json" in output_file:
            json.dump(rules, f, indent=4)
        else:
            yaml.dump(rules, f, sort_keys=False, default_flow_style=False)


@cli.command()
@click.argument("translator")
@click.argument("naf_file", type=click.Path(exists=True))
def translate_naf(matcher_spec: str, naf_file: str):
    """Translate text from a NAF file using specified rules.

    Args:
        matcher_spec: The type of matcher to use. Uses the common rules for the matcher factory.
        naf_file: Path to input NAF file
    """
    matcher = create_matcher(matcher_spec)
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
@click.argument("matcher_spec")
@click.argument("words", type=str, nargs=-1)
def translate_words(matcher_spec: str, words: List[str]):
    """Test word transcription using specified rules and engine.

    Args:
        matcher_spec: The type of matcher to use. Uses the common rules for the matcher factory.
        words: One or more words to transcribe
    """
    matcher = create_matcher(matcher_spec)
    translator = MatchingTranslator(matcher)
    translator = CachedTranslator(translator)

    input = [Word(text=w, attributes={"id": str(ix)}) for ix, w in enumerate(words)]
    input = clean_words(input, default_cleaners)
    output = translator.translate(input, emit="word")

    for result in output:
        print(result.word.text, " ".join([ph.sampa for ph in result.phonemes]))
