import re
from .data import RuleClass

MULTI_CHARACTER_RULE_PATTERN = re.compile(r'^[VC]=[a-z01]$')


def parse_rule(rule: str) -> str:
    """
    Parse a rule string into a RuleSpec object.
    """
    if isinstance(rule, int) or len(rule) == 1:
        return _parse_single_character_rule(rule)
    elif len(rule) == 3:
        return _parse_multi_character_rule(rule)
    else:
        raise ValueError(f"Invalid rule: {rule}")

def _parse_single_character_rule(rule: str) -> str:
    """
    Parse a single character rule string into a RuleSpec object.

    Such rules can either be a letter 'a' or a digit
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
    """
    Parse a multi-character rule string into a RuleSpec object.
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