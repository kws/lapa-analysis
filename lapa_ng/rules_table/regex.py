"""
Regular expression rule processing for LAPA-NG.

This module provides functionality for converting tabular rules into
regular expression patterns for phonetic transcription.
"""

import re
import yaml
from logging import getLogger
from lapa_ng.phonemes import PhonemeList
from lapa_ng.rules_table.table import TabularRule
from lapa_ng.rules_table.expressions import parse_rule
from lapa_ng.rules_regex.rules import RegexRuleSpec
from lapa_ng.rules_table.data import RuleClass

logger = getLogger(__name__)


def rule_to_regex(rule: TabularRule, phoneme_list: PhonemeList | None = None) -> RegexRuleSpec:
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
    pattern.extend([
        parse_rule(rule)
        for rule in rules
    ])

    # A bit of sanity checking
    for ix, parsed_rule in enumerate(pattern):
        if parsed_rule == "$":
            assert ix == len(pattern) - 1, "The dollar sign must be the last rule"

    # Create a regex pattern from the parsed rules
    pattern = "".join(pattern)

    # Replace the replaced phoneme with a capturing group
    replaced = rule.replaced
    match = re.match(f"^(\^?)({replaced})", pattern)

    if match is None:
        logger.warning(f"The replaced phoneme must be at the start of the pattern: {rule.rule_id}: {rule.rule} -> {replaced} must be in {pattern}")
        pattern_without_prefix = pattern[1:] if pattern.startswith("^") else pattern
        estimated_match = pattern_without_prefix[:len(replaced)]
        logger.warning(f"We will use an estimated match: {estimated_match}")
        replaced = estimated_match

    pattern = pattern.replace(replaced, f"({replaced})", 1)

    # Make sure the pattern is valid
    try:
        re.compile(pattern)
    except Exception as e:
        raise ValueError(f"Error compiling rule: {rule.rule_id}: {rule.rule} -> {pattern}") from e

    try:
        phonemes = [p.sampa for p in phoneme_list.split_phonemes(rule.replaceby)]
    except Exception as e:
        print(f"Error extracting phonemes for rule: {rule.rule_id}: {rule.rule} -> {rule.replaceby}")
        phonemes = [rule.replaceby]
    

    return RegexRuleSpec(
        id=rule.rule_id,
        pattern=pattern,
        replacement=" ".join(phonemes),
        meta={
            "original": rule.rule.replace("'", "")[1:-1],
            "description": rule.description,
            "priority": rule.priority,
        },
    )


