import re
from collections import defaultdict
from logging import getLogger

import yaml

from lapa_ng.phonemes import PhonemeList
from lapa_ng.rules_regex import RegexListMatcher, RegexMatcher, RegexRuleSpec
from lapa_ng.table_rules._expressions import parse_expression
from lapa_ng.table_rules._io import read_excel
from lapa_ng.table_rules._types import RuleClass, TabularRule

logger = getLogger(__name__)


def sort_rules_by_numeric_priority(rules: list[TabularRule]) -> list[TabularRule]:
    """Sort rules by their numeric priority.

    Rules are sorted first by letter, then by prefix status, then by default status,
    and finally by priority value.

    Args:
        rules: List of rules to sort

    Returns:
        Sorted list of rules
    """
    return sorted(
        rules,
        key=lambda x: (
            x.letter,
            x.rule_class != RuleClass.PREFIX,
            x.is_default,
            x.priority,
        ),
    )


def sort_rules_by_alpha_priority(rules: list[TabularRule]) -> list[TabularRule]:
    """Sort rules by their priority, treating priorities as strings.

    This function mimics the original sort order of the code by converting
    priorities to strings before comparison.

    Args:
        rules: List of rules to sort

    Returns:
        Sorted list of rules
    """
    return sorted(
        rules,
        key=lambda x: (
            x.letter,
            x.rule_class != RuleClass.PREFIX,
            x.is_default,
            str(x.priority),
        ),
    )


def check_rules_for_duplicate_priorities(
    rules: list[TabularRule],
) -> dict[int, list[TabularRule]]:
    """Check rules for duplicate priorities.

    Args:
        rules: List of rules to check

    Returns:
        Dictionary mapping priority tuples to lists of rules with that priority
    """
    rules_by_priority = defaultdict(list)
    for rule in rules:
        priority = (
            rule.letter,
            rule.rule_class != RuleClass.PREFIX,
            rule.is_default,
            rule.priority,
        )
        rules_by_priority[priority].append(rule)

    duplicates = {k: v for k, v in rules_by_priority.items() if len(v) > 1}
    return duplicates


def load_regex_matcher_list(
    rules_file: str,
    sheet_name: str | int | None = None,
    sort_function: callable = sort_rules_by_numeric_priority,
) -> list[RegexMatcher]:
    """Load a set of excel rules and convert them to a list of RegexMatchers."""
    rules = read_excel(rules_file, sheet_name=sheet_name)

    duplicates = check_rules_for_duplicate_priorities(rules)
    for k, v in duplicates.items():
        logger.warning(
            f"For letter {k[0]} and priority {k[3]} there are {len(v)} duplicates: {', '.join(r.rule_id for r in v)}"
        )

    regex_list = []
    for r in sort_function(rules):
        try:
            regex_list.append(table_rule_to_regex_spec(r))
        except Exception as e:
            logger.error(f"Error converting rule {r.rule_id} to regex: {e}")

    regex_matchers = [RegexMatcher(r) for r in regex_list]
    return regex_matchers


def load_matcher(
    rules_file: str,
    sheet_name: str | int | None = None,
    sort_function: callable = sort_rules_by_numeric_priority,
) -> RegexListMatcher:
    """
    Load a set of excel rules and convert them to a RegexListMatcher.
    """
    return RegexListMatcher(
        load_regex_matcher_list(rules_file, sheet_name, sort_function)
    )


def table_rule_to_regex_spec(
    rule: TabularRule, phoneme_list: PhonemeList | None = None
) -> RegexRuleSpec:
    """Convert a tabular rule into a regular expression specification.

    This function takes a TabularRule and converts it into a RegexRuleSpec,
    which includes the regular expression pattern and replacement phonemes.

    Args:
        rule: The tabular rule to convert
        phoneme_list: Optional phoneme list for phoneme validation

    Returns:
        A RegexRuleSpec containing the pattern and replacement information

    Raises:
        ValueError: If the rule pattern is invalid or cannot be compiled
    """
    if phoneme_list is None:
        phoneme_list = PhonemeList.default()

    pattern = []
    if rule.rule_class == RuleClass.PREFIX:
        pattern.append("^")

    # We use yaml to parse the rule syntax since the format is the same as the one used in the rules table
    rules = yaml.safe_load(rule.rule)
    pattern.extend([parse_expression(rule) for rule in rules])

    # A bit of sanity checking
    for ix, parsed_rule in enumerate(pattern):
        if parsed_rule == "$":
            assert ix == len(pattern) - 1, "The dollar sign must be the last rule"

    # Create a regex pattern from the parsed rules
    pattern = "".join(pattern)

    # Replace the replaced phoneme with a capturing group
    replaced = rule.replaced
    match = re.match(rf"^(\^?)({re.escape(replaced)})", pattern)

    if match is None:
        logger.warning(
            f"The replaced phoneme must be at the start of the pattern: {rule.rule_id}: {rule.rule} -> {replaced} must be in {pattern}"
        )
        pattern_without_prefix = pattern[1:] if pattern.startswith("^") else pattern
        estimated_match = pattern_without_prefix[: len(replaced)]
        logger.warning(f"We will use an estimated match: {estimated_match}")
        replaced = estimated_match

    pattern = pattern.replace(replaced, f"({replaced})", 1)

    # Make sure the pattern is valid
    try:
        re.compile(pattern)
    except Exception as e:
        raise ValueError(
            f"Error compiling rule: {rule.rule_id}: {rule.rule} -> {pattern}"
        ) from e

    try:
        phonemes = phoneme_list.split_phonemes(rule.replaceby)
    except Exception as e:
        print(
            f"Error extracting phonemes for rule: {rule.rule_id}: {rule.rule} -> {rule.replaceby}"
        )
        phonemes = [rule.replaceby]

    return RegexRuleSpec(
        id=rule.rule_id,
        pattern=pattern,
        replacement=phonemes,
        meta={
            "original": rule.rule.replace("'", "")[1:-1],
            "description": rule.description,
            "priority": rule.priority,
        },
    )


class TableRulesMatcher(RegexListMatcher):
    """A matcher that uses a list of regex matchers to match words.

    This class extends the RegexListMatcher by providing a helpful initialiser
    that loads the rules from an Excel file and converts them into a list of
    RegexMatchers. This gives us a similar interface to the ClassicMatcher.
    """

    def __init__(
        self,
        rules_file: str,
        sheet_name: str | int | None = None,
        sort_function: callable = sort_rules_by_numeric_priority,
    ):
        """Initialise the TableRulesMatcher.

        Args:
            rules_file: The path to the Excel file containing the rules
            sheet_name: The name of the sheet in the Excel file containing the rules
            sort_function: The function to use to sort the rules
        """
        matcher_list = load_regex_matcher_list(
            rules_file, sheet_name=sheet_name, sort_function=sort_function
        )
        super().__init__(matcher_list)
