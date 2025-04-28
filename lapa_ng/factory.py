"""Factory module for creating matchers in LAPA-NG.

This module provides a factory function to create different types of matchers
based on a specification string. The specification string follows the format:

    [prefix:][filename[#sheet]]

Where:
- prefix: Optional prefix indicating the type of matcher ('ng' or 'classic')
- filename: Path to the rules file (Excel or YAML)
- sheet: Optional sheet name for Excel files

Examples:
    ng:rules.xlsx#RULES      # Next-gen matcher with specific sheet
    classic:rules.xlsx       # Classic matcher, default sheet
    rules.xlsx#RULES         # Next-gen matcher (default prefix)
"""

import re
from dataclasses import dataclass
from urllib.parse import parse_qs

from lapa_ng.table_rules import (
    sort_rules_by_alpha_priority,
    sort_rules_by_numeric_priority,
)
from lapa_ng.types import Matcher

PTN_MATCHER_SPEC = re.compile(r"^((ng|classic):)?(.*?)(#(.*?))?(\?.*)?$")


@dataclass
class MatcherSpec:
    prefix: str
    filename: str
    section: str
    options: str

    @property
    def qs(self) -> dict:
        if self.options is None:
            return {}
        if self.options.startswith("?"):
            return parse_qs(self.options[1:])
        raise ValueError(f"Invalid options: {self.options}")

    @property
    def qs_flat(self) -> dict:
        return {k: v[0] for k, v in self.qs.items()}


def parse_matcher_spec(matcher_spec: str) -> MatcherSpec:
    """Parse a matcher specification string into its components.

    This function parses the specification string into its prefix, filename,
    sheet name, and options.

    Args:
        matcher_spec: The specification string in format '[prefix:][filename[#sheet]]'
    """
    match = PTN_MATCHER_SPEC.match(matcher_spec)
    if not match:
        raise ValueError(f"Invalid matcher specification: {matcher_spec}")

    prefix = match.group(2) or "ng"
    filename = match.group(3)
    section = match.group(5)
    options = match.group(6)

    return MatcherSpec(prefix, filename, section, options)


def create_matcher(matcher_spec: str) -> Matcher:
    """Create a matcher based on a specification string.

    This factory function creates the appropriate matcher based on the
    specification string. It supports both the next-generation ('ng')
    and classic matchers.

    Args:
        matcher_spec: Specification string in format '[prefix:][filename[#sheet]]'
            - prefix: Optional prefix ('ng' or 'classic')
            - filename: Path to rules file
            - sheet: Optional sheet name for Excel files

    Returns:
        A Matcher instance configured according to the specification

    Raises:
        ValueError: If the prefix is unknown or the specification is invalid

    Examples:
        >>> create_matcher('ng:rules.xlsx#RULES')  # Next-gen matcher
        >>> create_matcher('classic:rules.xlsx')   # Classic matcher
        >>> create_matcher('rules.xlsx#RULES')     # Default (ng) matcher
        >>> create_matcher('ng:rules.xlsx#RULES?sort=numeric')  # Next-gen matcher with numeric sort
    """
    spec = parse_matcher_spec(matcher_spec)

    if spec.prefix == "ng":
        from lapa_ng.table_rules import TableRulesMatcher

        options = spec.qs_flat
        sort = options.get("sort", "numeric")
        if sort not in ["alpha", "numeric"]:
            raise ValueError(f"Sort option must be 'alpha' or 'numeric'")
        sort_function = (
            sort_rules_by_numeric_priority
            if sort == "numeric"
            else sort_rules_by_alpha_priority
        )
        return TableRulesMatcher(
            spec.filename, sheet_name=spec.section, sort_function=sort_function
        )

    elif spec.prefix == "classic":
        from lapa_ng.classic import ClassicMatcher

        return ClassicMatcher(spec.filename, sheet_name=spec.section)

    else:
        raise ValueError(f"Unknown matcher prefix: {spec.prefix}")
