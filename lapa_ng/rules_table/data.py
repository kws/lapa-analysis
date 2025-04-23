from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class RuleClass(Enum):
    """
    An enumeration of the possible rule classes.
    """
    VOWEL = 'V'
    CONSONANT = 'C'
    PREFIX = 'P'


@dataclass
class TabularRule:
    """
    A class representing a rule from a tabular data source.

    :param rule_id: The ID of the rule
    :type rule_id: str

    :param rule_class: The class of the rule (VOWEL, CONSONANT, PREFIX)
    :type rule_class: RuleClass

    :param letter: The initial letter of the rule
    :type letter: str

    :param is_default: Whether the rule is a default rule
    :type is_default: bool

    :param priority: The priority of the rule
    :type priority: int

    :param description: The description of the rule
    :type description: str

    :param rule: The rule definition
    :type rule: str

    :param replaced: The letter sequence to be replaced
    :type replaced: str

    :param replaceby: Replacement letter sequence
    :type replaceby: str
    """
    rule_id: str
    rule_class: RuleClass
    letter: str
    is_default: bool
    priority: int
    description: str
    rule: str
    replaced: str
    replaceby: str