import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Generator

import xlrd
import yaml

from lapa_classic.sampify import Rules, Sampify
from lapa_ng.phonemes import PhonemeList
from lapa_ng.types import ContextualMatchResult, Matcher, MatchResult, Word


class _CallInterceptor:

    def __init__(self, func):
        self.func = func
        self.trace = []

    def __call__(self, *args, **kwargs):
        value = self.func(*args, **kwargs)
        self.trace.append((args, kwargs, value))
        return value

    def pop(self):
        value = tuple(self.trace)
        self.trace.clear()
        return value


@dataclass
class RuleId:
    rule_id: str
    expression: str
    description: str
    replaced: str
    replaceby: str
    first_letter: str = ""

    def __post_init__(self):
        expression = yaml.safe_load(self.expression)
        self.first_letter = expression[0].lower()


def excel_to_rules(input_file: str, sheet_name: str | None = None) -> dict:
    """
    Read an Excel file and convert it to a dictionary of rules.

    From: :py:func:`lapa_classic.sampify._xlsx_to_csv`
    """
    file_id = Path(input_file).name

    wb = xlrd.open_workbook(input_file)
    sheet_names = wb.sheet_names()
    if sheet_name:
        file_id = f"{file_id}:{sheet_name}"
        if sheet_name not in sheet_names:
            raise ValueError(f"Sheet {sheet_name} not found in {input_file}")
    else:
        if len(sheet_names) != 1:
            raise ValueError(
                f"Multiple sheets found in {input_file}, please specify which one to use"
            )
        sheet_name = sheet_names[0]

    sh = wb.sheet_by_name(sheet_name)

    rule_ids = []

    # Although NG has a reader - we use the original approach to avoid unintentional differences
    with NamedTemporaryFile() as temp_file:
        with open(temp_file.name, "w") as f:
            wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL, delimiter=";")
            for rownum in range(sh.nrows):
                row_values = sh.row_values(rownum)
                wr.writerow(row_values)

                rule_id = f"{file_id}:{rownum + 1}"
                rule_ids.append(
                    RuleId(
                        rule_id,
                        description=row_values[4],
                        expression=row_values[5],
                        replaced=row_values[6],
                        replaceby=row_values[7],
                    )
                )

        rules = Rules()
        parsed_rules = rules._read_csv(temp_file.name)

    return parsed_rules, rule_ids


class ClassicMatcher(Matcher):

    def __init__(self, file: str, sheet_name: str | None = None):
        rules, rule_ids = excel_to_rules(file, sheet_name)

        self.rule_ids = {
            (rule.first_letter, rule.description): rule for rule in rule_ids
        }

        self.sampify = Sampify()
        self.sampify._add_rules(rules)
        self.sampify._test_rule = _CallInterceptor(self.sampify._test_rule)
        self.sampify._apply_rule = _CallInterceptor(self.sampify._apply_rule)
        self.phoneme_list = PhonemeList.default()

    @property
    def id(self) -> str:
        """Return a string identifier for this matcher."""
        return f"ClassicMatcher(rules={len(self.rule_ids)})"

    def __repr__(self) -> str:
        """Return a string representation of this matcher."""
        return f"ClassicMatcher(rules={len(self.rule_ids)})"

    def __len__(self) -> int:
        """Return the number of rules in this matcher."""
        return len(self.rule_ids)

    def _rule_for_meta(self, meta):
        first_letter = meta["rule"][0]
        return self.rule_ids.get((first_letter, meta["description"]))

    def match(self, word: Word, start: int) -> Generator[MatchResult, None, None]:
        if start != 0:
            return []

        translated = self.sampify.translate(word.text)
        trace = self.sampify._apply_rule.pop()
        candidates = self.sampify._test_rule.pop()

        # Position Mapper (this function doesn't trace position in the word, only the position in the match)
        # So we need to figure out which part of the original word is translates back to the match
        position_mapper = {}

        # Collect trace by position
        trace_by_position = {}
        match_so_far = ""
        for args, kwargs, value in trace:
            log, sampa, position, rule, rulenum = args
            # position_mapper[len(match_so_far)] = position
            position_mapper[position] = len(match_so_far)

            rule_id = self._rule_for_meta(rule)
            match_so_far += rule_id.replaced
            trace_by_position[position] = (
                rule_id.replaced,
                rule_id.replaceby,
                match_so_far,
                word.text[len(match_so_far) :],
                rule_id.rule_id,
                rule_id.description,
            )

        # Collect all traces for each position
        candidates_by_position = defaultdict(list)
        for args, kwargs, value in candidates:
            pos = args[4]
            candidates_by_position[pos].append((args, kwargs, value))

        # Filter to only traces prior to the first match - for some reason the code tests all rules even after a match has been found
        for pos, trace in candidates_by_position.items():
            args = [t[0] for t in trace]
            kwargs = [t[1] for t in trace]
            results = [t[2] for t in trace]
            try:
                first_match = results.index(True)
                args = args[:first_match]
            except ValueError:
                pass

            regexes = [self._rule_for_meta(r[3]) for r in args]
            regexes = [r.rule_id if r else "missing rule" for r in regexes]
            candidates_by_position[pos] = regexes

        for pos, value in trace_by_position.items():
            ph = self.phoneme_list.split_phonemes(value[1], ignore_errors=True)
            candidates = candidates_by_position[pos]

            yield ContextualMatchResult(
                word=word,
                phonemes=ph,
                start=pos,
                matched=word.text,
                remainder=value[3],
                rule_id=value[4],
                rules_attempted=candidates,
            )
