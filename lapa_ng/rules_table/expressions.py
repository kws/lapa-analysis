"""
Rule expression parsing for LAPA-NG.

This module provides functionality for parsing and converting rule expressions
into their corresponding phonetic patterns.
"""

import re
from .data import RuleClass

MULTI_CHARACTER_RULE_PATTERN = re.compile(r'^[VC]=[a-z01]$')


def parse_rule(rule: str) -> str:
    """Parse a rule string into its corresponding pattern.
    
    This function handles both single-character and multi-character rules,
    converting them into the appropriate phonetic pattern.
    
    Args:
        rule: The rule string to parse
        
    Returns:
        The parsed phonetic pattern
        
    Raises:
        ValueError: If the rule format is invalid
    """
    if isinstance(rule, int) or len(rule) == 1:
        return _parse_single_character_rule(rule)
    elif len(rule) == 3:
        return _parse_multi_character_rule(rule)
    else:
        raise ValueError(f"Invalid rule: {rule}")

def _parse_single_character_rule(rule: str) -> str:
    """Parse a single character rule into its pattern.
    
    Single character rules can be either:
    - A letter (returned as-is)
    - A digit (0 or 1, converted to special patterns)
    
    Args:
        rule: The single character rule to parse
        
    Returns:
        The corresponding phonetic pattern
        
    Raises:
        ValueError: If the rule is an invalid digit
    """
    # Let's first check if the rule is a digit
    if type(rule) == int or rule.isdigit():
        rule = int(rule)
        if rule == 0:
            return "$"
        elif rule == 1:
            return "."
        else:
            raise ValueError(f"Invalid rule: {rule}")

    # Otherwise we assume it's a letter and just return that 
    return rule

def _parse_multi_character_rule(rule: str) -> str:
    """Parse a multi-character rule into its pattern.
    
    Multi-character rules follow the format [VC]=[a-z01], where:
    - V/C indicates vowel/consonant class
    - The letter or digit specifies the pattern
    
    Args:
        rule: The multi-character rule to parse
        
    Returns:
        The corresponding phonetic pattern
        
    Raises:
        AssertionError: If the rule doesn't match the expected pattern
    """
    assert MULTI_CHARACTER_RULE_PATTERN.match(rule), f"Rule doesn't match the expected pattern: {rule}"
    rule_class, letter = rule.split('=')
    rule_class = RuleClass(rule_class)
    if letter in "01":
        # Flip the rule class if the letter is a 0, i.e. NOT CONSONANT, or NOT VOWEL
        if letter == "0":
            rule_class = RuleClass.VOWEL if rule_class == RuleClass.CONSONANT else RuleClass.CONSONANT

        return "[:consonant:]" if rule_class == RuleClass.CONSONANT else "[:vowel:]"

    else:
        return letter