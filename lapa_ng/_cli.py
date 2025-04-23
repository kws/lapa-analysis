"""
Command-line interface for the LAPA-NG package.

This module provides various commands for testing, converting, and processing
rules and text using the LAPA-NG phonetic transcription system.
"""

import json
import shutil
from typing import List
import click
import yaml

def represent_none(self, _):
    """YAML representer for None values."""
    return self.represent_scalar('tag:yaml.org,2002:null', '')

yaml.add_representer(type(None), represent_none)

@click.group()
def cli():
    """LAPA-NG command-line interface for phonetic transcription and rule processing."""
    pass

@cli.command()
@click.argument("rule_file", type=click.Path(exists=True))
@click.argument("words", type=str, nargs=-1)
@click.option("--engine", type=click.Choice(["sampify", "lapa"]), default="lapa")
def test_word(words: List[str], rule_file: str, engine: str):
    """Test word transcription using specified rules and engine.
    
    Args:
        words: One or more words to transcribe
        rule_file: Path to the rules file
        engine: Transcription engine to use ('sampify' or 'lapa')
    """
    if engine == "sampify":
        from classes.sampify import Sampify
        rules = Sampify(rule_file)
        translations = [rules.translate(w) for w in words]
        for word, translation in zip(words, translations):
            print(f"{word} -> {translation}")
    else:
        from lapa_ng.rules.matchers import match_word, load_rules
        rules = load_rules(rule_file)

        for word in words:
            matches = list(match_word(word, rules))
            translations = " ".join([m.match_result.phonemes for m in matches])
            print(f"{word} -> {translations}")

@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--format", type=click.Choice(["csv", "json"]), default="excel")
def dump_excel(input_file: str, output_file: str, format: str):
    """Convert Excel rules file to CSV or JSON format.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output file
        format: Output format ('csv' or 'json')
    """
    import xlrd, csv
    from tempfile import NamedTemporaryFile
    from classes.sampify import Rules

    wb = xlrd.open_workbook(input_file)
    sh = wb.sheet_by_name('RULES')

    with NamedTemporaryFile() as temp_file:
        with open(temp_file.name, 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL, delimiter=';')
            for rownum in range(sh.nrows):
                wr.writerow(sh.row_values(rownum))
        
        if format == "csv":
            shutil.copy(temp_file.name, output_file)
        else:
            rules = Rules()
            parsed_rules = rules._read_csv(temp_file.name)
            with open(output_file, 'w') as f:
                json.dump(parsed_rules, f, indent=4)

@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--sheet", type=str)
def convert_excel(input_file: str, output_file: str, sheet:str|None):
    """Convert Excel rules file to YAML format.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output YAML file
        sheet: Optional sheet name to convert
    """
    from lapa_ng.rules_table.table import read_excel, rules_to_list
    rules = read_excel(input_file, sheet_name=sheet)
    specs = rules_to_list(rules)

    with open(output_file, 'w') as f:
        yaml.dump(specs, f, sort_keys=False, default_flow_style=False)

@cli.command()
@click.argument("naf_file", type=click.Path(exists=True))
@click.argument("rule_file", type=click.Path(exists=True), default="regexrules.yml")
def translate_naf(naf_file: str, rule_file: str):
    """Translate text from a NAF file using specified rules.
    
    Args:
        naf_file: Path to input NAF file
        rule_file: Path to rules file
    """
    from lapa_ng.naf import parse_naf
    from lapa_ng.rules.matchers import ReplacementEngine, load_rules
    import csv 

    rules = load_rules(rule_file)
    engine = ReplacementEngine(rules)

    with open("output.csv", "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, delimiter=',')
        writer.writerow(["id", "text", "start", "matched", "ix", "phoneme", "rule_id", "rules_attempted"])

        for text in parse_naf(naf_file):
            attribs = text.attributes
            text = text.text if text.text else ""
            text = text.strip()
            translations = engine.translate(text.lower())
            for t in translations:
                for ix, ph in enumerate(t.match_result.phonemes.split(" ")):
                    mr = t.match_result
                    writer.writerow([attribs.get("id", ""), text, mr.start, mr.matched, ix, ph, t.rule_id, len(t.rules_attempted)])
