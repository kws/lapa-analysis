"""
Table-based rule processing for LAPA-NG.

This module provides functionality for reading and processing rules from
tabular data sources like Excel and CSV files.
"""

from logging import getLogger
from pathlib import Path
from typing import Generator

import numpy as np
import pandas as pd

from lapa_ng.table_rules._types import RuleClass, TabularRule

logger = getLogger(__name__)

PathOrString = str | Path


def _to_str(obj: object) -> str:
    """Convert an object to a string, handling special cases.

    Args:
        obj: The object to convert

    Returns:
        String representation of the object, or None for NaN values

    Raises:
        ValueError: If the object is not a string
    """
    if isinstance(obj, float) and np.isnan(obj):
        return None
    if not isinstance(obj, str):
        raise ValueError(f"Expected a string, got {type(obj)}: {obj}")
    return obj


def dataframe_to_rules(
    df: pd.DataFrame, file_id: str | None = None, start_ix: int = 0
) -> Generator[TabularRule, None, None]:
    """Convert a pandas DataFrame to a sequence of TabularRule objects.

    Args:
        df: DataFrame containing rule data
        file_id: Optional identifier for the source file
        start_ix: Starting index for rule numbering

    Yields:
        TabularRule objects created from the DataFrame rows
    """
    for row_ix, row in df.iterrows():
        # Convert the row to a list for simpler access
        row = [row.iloc[i] for i in range(len(row))]

        rule_class = RuleClass(row[0])
        letter = row[1]
        is_default = row[2]
        assert is_default in [
            "default",
            "rules",
        ], f"Invalid default value: {is_default}. Must be either 'default' or 'rules'"
        is_default = is_default == "default"

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
            replaceby=_to_str(row[7]),
        )


def read_csv(
    file_path: PathOrString, field_separator: str = ",", skiprows: int = 0
) -> list[TabularRule]:
    """Read a CSV file and return a list of TabularRule objects.

    Args:
        file_path: Path to the CSV file to read
        field_separator: Character used to separate fields in the CSV file
        skiprows: Number of rows to skip from the start of the file

    Returns:
        List of TabularRule objects created from the CSV data
    """
    df = pd.read_csv(file_path, sep=field_separator, skiprows=skiprows)
    return list(
        dataframe_to_rules(df, file_id=Path(file_path).name, start_ix=skiprows + 1)
    )


def read_excel(
    file_path: PathOrString, sheet_name: str | int | None = None
) -> list[TabularRule]:
    """Read an Excel file and return a list of TabularRule objects.

    Args:
        file_path: Path to the Excel file to read
        sheet_name: Name or index of the sheet to read

    Returns:
        List of TabularRule objects created from the Excel data

    Raises:
        ValueError: If multiple sheets are found and no sheet_name is specified
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    if isinstance(df, dict):
        raise ValueError(
            f"Multiple sheets found in the Excel file. Please specify the sheet name or index from: {', '.join(df.keys())}"
        )

    file_name = Path(file_path).name
    if sheet_name:
        file_name = f"{file_name}:{sheet_name}"
    return list(dataframe_to_rules(df, file_id=file_name, start_ix=2))
