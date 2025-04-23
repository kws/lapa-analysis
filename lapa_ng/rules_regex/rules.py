from pathlib import Path
import re
from typing import Any
from lapa_ng.rules.matchers import Matcher, MatchResult
from dataclasses import dataclass
import yaml

DEFAULT_CHARACTER_CLASSES = {
    "vowel": "aeiouy",
    "consonant": "bcdfghjklmnpqrstvwxz",
    "digit": "0123456789",
    "punctuation": ".,!?:;",
}

@dataclass(frozen=True)
class RegexRuleSpec:
    """
    A class representing a rule specification used to initialise a RegexMatcher.
    """
    id: str
    pattern: re.Pattern
    replacement: str
    meta: dict[str, Any]
    

class RegexMatcher(Matcher):
    """
    A class representing a matcher that uses a regex pattern to match a word.

    RegexMatchers have a few extras to allow for optimisation when matching. 
    
    First of all there are two types of matchers,
    those that only match at the start of a word, and those that can match anywhere in a word.

    Secondly, the matcher exposes the "match_group" which is the group that is matched by the regex.

    When using the regex specific engine, rules are first filtered so only relevant rules based on these two properties are attempted.
    """

    __slots__ = ('id', 'replacement', 'match_group', 'prefix', 'rule')
    
    def __init__(self, id: str, rule: str, replacement: str, meta: dict[str, Any] = None):
        self.id = id
        self.replacement = replacement
        self.meta = meta

        # For optimisation, we extract the match group from the rule.
        match = re.search(r'\((.*)\)', rule)
        if match:
            self.match_group = match.group(1)
        else:
            raise ValueError(f"No match group found in rule {self.id}: {rule}")

        # If the rule starts with a caret, it is a prefix rule. We only then match for start == 0
        if rule.startswith('^'):
            self.prefix = True
            self.rule = rule
        else:
            self.prefix = False
            self.rule = '^' + rule

        # Replace the character classes with the actual characters
        for class_name, characters in DEFAULT_CHARACTER_CLASSES.items():
            self.rule = re.sub(rf"\[:{class_name}:\]", f"[{characters}]", self.rule)

        self.rule = re.compile(self.rule)

    def match(self, word: str, start:int) -> MatchResult | None:
        if self.prefix and start != 0:
            return None

        test_word = word[start:]
        match = self.rule.match(test_word)
        if not match:
            return None

        replacement_part = match.group(1)
        replacment_length = len(replacement_part)

        remainder = word[start + replacment_length:]

        return MatchResult(matched = replacement_part, phonemes = self.replacement, word = word, start = start, remainder = remainder)


def load_specs(rule_file: str | Path) -> tuple[RegexRuleSpec, ...]:
    """
    Load a YAML file containing rule specifications and return a tuple of RegexRuleSpec objects.
    """
    with open(rule_file, 'r') as f:
        rules = yaml.safe_load(f)

    return tuple([RegexRuleSpec(**rule) for rule in rules])

def load_matchers(rule_file: str | Path) -> tuple[RegexMatcher, ...]:
    """
    Load a YAML file containing rule specifications and return a tuple of RegexMatcher objects.
    """
    return tuple([RegexMatcher(spec) for spec in load_specs(rule_file)])
