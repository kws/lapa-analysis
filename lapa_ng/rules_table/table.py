from collections import defaultdict
from pathlib import Path
from typing import Counter, Generator
import pandas as pd
import numpy as np

from lapa_ng.rules_table.data import RuleClass, TabularRule

PathOrString = str | Path


def _to_str(obj: object) -> str:
    """
    Convert an object to a string. Replaces nan with None
    """
    if isinstance(obj, float) and np.isnan(obj):
        return None 
    if not isinstance(obj, str):
        raise ValueError(f"Expected a string, got {type(obj)}: {obj}")
    return obj

def dataframe_to_rules(df: pd.DataFrame, file_id: str|None = None, start_ix: int = 0) -> Generator[TabularRule, None, None]:
    for row_ix, row in df.iterrows():
        # Convert the row to a list for simpler access
        row = [row.iloc[i] for i in range(len(row))]

        rule_class = RuleClass(row[0])
        letter = row[1]
        is_default = row[2]
        assert is_default in ['default', 'rules'], f"Invalid default value: {is_default}. Must be either 'default' or 'rules'"
        is_default = is_default == 'default'

        priority = int(row[3])
        rule_id = f"{file_id}:{row_ix + start_ix}" if file_id else row_ix + start_ix

        yield TabularRule(
            rule_id=rule_id,
            rule_class=rule_class,
            letter=letter,
            is_default=is_default,
            priority=priority,
            description=row[4],
            rule=row[5],
            replaced=_to_str(row[6]),
            replaceby=_to_str(row[7])
        )


def read_csv(file_path: PathOrString, field_separator: str = ',', skiprows: int = 0) -> list[TabularRule]:
    """Read a CSV file and return a list of TabularRule objects.

    :param file_path: Path to the CSV file to read
    :type file_path: PathOrString

    :param field_separator: Character used to separate fields in the CSV file, defaults to ','
    :type field_separator: str
    
    :param skiprows: Number of rows to skip from the start of the file, defaults to 0
    :type skiprows: int
    
    :return: List of TabularRule objects created from the CSV data
    :rtype: List[TabularRule]
    """
    df = pd.read_csv(file_path, sep=field_separator, skiprows=skiprows)
    return list(dataframe_to_rules(df, file_id=Path(file_path).name, start_ix=skiprows+1))



def read_excel(file_path: PathOrString, sheet_name: str | int | None = None) -> list[TabularRule]:
    """Read an Excel file and return a list of TabularRule objects.

    :param file_path: Path to the Excel file to read
    :type file_path: PathOrString

    :param sheet_name: Name of the sheet to read from the Excel file, defaults to None (read all sheets)
    :type sheet_name: str | int | None

    :return: List of TabularRule objects created from the Excel data
    :rtype: List[TabularRule]
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    if isinstance(df, dict):
        raise ValueError(f"Multiple sheets found in the Excel file. Please specify the sheet name or index from: {', '.join(df.keys())}")
    
    file_name = Path(file_path).name
    if sheet_name:
        file_name = f"{file_name}:{sheet_name}"
    return list(dataframe_to_rules(df, file_id=file_name, start_ix=2))

def sort_rules_by_numeric_priority(rules: list[TabularRule]) -> list[TabularRule]:
    """
    Sort rules by their numeric priority. Rules are sorted first by letter, then by prefix, then by default, and finally by priority.
    """
    return sorted(rules, key=lambda x: (x.letter, x.rule_class != RuleClass.PREFIX, x.is_default, x.priority))

def sort_rules_by_alpha_priority(rules: list[TabularRule]) -> list[TabularRule]:
    """
    Sort rules by their numeric priority. Rules are sorted first by letter, then by prefix, then by default, and finally by priority.

    Priorities are converted to strings to mimmic the original sort order of the code.
    """
    return sorted(rules, key=lambda x: (x.letter, x.rule_class != RuleClass.PREFIX, x.is_default, str(x.priority)))

def check_rules_for_duplicate_priorities(rules: list[TabularRule]) -> dict[int, list[TabularRule]]:
    """
    Check rules for duplicate priorities.
    """
    rules_by_priority = defaultdict(list)
    for rule in rules:
        priority = (rule.letter, rule.rule_class != RuleClass.PREFIX, rule.is_default, rule.priority)
        rules_by_priority[priority].append(rule)

    duplicates = {k: v for k, v in rules_by_priority.items() if len(v) > 1}
    return duplicates

