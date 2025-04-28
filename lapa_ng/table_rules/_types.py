from dataclasses import dataclass
from enum import Enum


class RuleClass(Enum):
    """Enumeration of possible rule classes.

    This enum defines the different types of rules that can be processed:
    - VOWEL: Rules for vowel sounds
    - CONSONANT: Rules for consonant sounds
    - PREFIX: Rules for prefix patterns
    """

    VOWEL = "V"
    CONSONANT = "C"
    PREFIX = "P"


@dataclass
class TabularRule:
    """Represents a rule from a tabular data source.

    This class encapsulates all the information needed to define a phonetic
    transcription rule, including its type, priority, and transformation details.

    Attributes:
        rule_id: Unique identifier for the rule
        rule_class: Type of rule (VOWEL, CONSONANT, or PREFIX)
        letter: Initial letter that the rule applies to
        is_default: Whether this is a default rule
        priority: Priority value for rule ordering
        description: Human-readable description of the rule
        rule: The rule pattern or definition
        replaced: Letter sequence to be replaced
        replaceby: Replacement letter sequence
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
