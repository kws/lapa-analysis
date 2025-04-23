from pathlib import Path
from tempfile import TemporaryDirectory
import os

from lapa_ng.rules_table.table import read_csv, read_excel
from lapa_ng.rules_table.expressions import parse_rule
from lapa_ng.rules_table.data import RuleClass, TabularRule
from lapa_ng.rules_table.regex import rule_to_regex

def test_read_csv():
    """
    Test that the read_csv function can read a CSV file and return a list of rules.
    """
    with TemporaryDirectory() as temp_dir:

        csv_file_path = os.path.join(temp_dir, 'test.csv')

        with open(csv_file_path, 'w') as f:
            f.write('V/C/P,letter,default/rules,number,description,rule,replaced,replaceby\n')
            f.write('V,a,default,0,no rule found,["a"],a,A\n')
            f.write('C,b,rules,1,simple replacement,"[""b"", ""V=1""]",b,B\n')

        rules = read_csv(csv_file_path)
        
        assert len(rules) == 2

        first_rule = rules[0]
        assert first_rule.rule_class == RuleClass.VOWEL
        assert first_rule.letter == 'a'
        assert first_rule.is_default == True
        assert first_rule.priority == 0
        assert first_rule.description == 'no rule found'
        assert first_rule.rule == '["a"]'
        assert first_rule.replaced == 'a'
        assert first_rule.replaceby == 'A'

        second_rule = rules[1]
        assert second_rule.rule_class == RuleClass.CONSONANT
        assert second_rule.letter == 'b'
        assert second_rule.is_default == False
        assert second_rule.priority == 1
        assert second_rule.description == 'simple replacement'
        assert second_rule.rule == '["b", "V=1"]'


def test_read_excel(fixtures_path):
    """
    Test that the read_excel function can read an Excel file and return a list of rules.

    This should be done properly as it is currently more of an integration test.
    """
    source_path = fixtures_path / 'RULES_A_V1.5.xls'
    rules = read_excel(source_path, sheet_name='RULES')

    assert len(rules) == 304

    compiled_rules = [rule_to_regex(rule) for rule in rules]

    assert len(compiled_rules) == 304



def test_parse_rule():
    parse_rule("a") == "a"
    parse_rule("1") == "."
    parse_rule("0") == "$"
    parse_rule("C=b") == "b"
    parse_rule("V=b") == "b"
    parse_rule("V=0") == "[bcdfghjklmnpqrstvwxyz]"
    parse_rule("V=1") == "[aeiou]"
    parse_rule("C=0") == "[aeiou]"
    parse_rule("C=1") == "[bcdfghjklmnpqrstvwxyz]"


def test_prefix_rule():
    """
    Test that the rule_to_spec function can convert a rule to a RuleSpec object.
    """
    tabular_rule = TabularRule(
        rule_id="test:0",
        rule_class=RuleClass.PREFIX,
        letter="a",
        is_default=True,
        priority=0,
        description="",
        rule='["a", "C=b", "C=c", 0]',
        replaced="abc",
        replaceby="ABC",
    )

    spec = rule_to_regex(tabular_rule)
    assert spec.pattern == "^(abc)$"

    tabular_rule.rule = '["a", "C=b", "C=c", 1]'
    spec = rule_to_regex(tabular_rule)
    assert spec.pattern == "^(abc)."

    tabular_rule.rule = '["a", "C=b", "C=c"]'
    spec = rule_to_regex(tabular_rule)
    assert spec.pattern == "^(abc)"


def test_character_class_rules():
    """
    Test that the rule_to_spec function can convert a rule to a RuleSpec object.
    """
    tabular_rule = TabularRule(
        rule_id="test:0",
        rule_class=RuleClass.PREFIX,
        letter="a",
        is_default=True,
        priority=0,
        description="",
        rule='["a", "C=1", "C=0"]',
        replaced="a",
        replaceby="#",
    )

    spec = rule_to_regex(tabular_rule)
    assert spec.pattern == "^(a)[:consonant:][:vowel:]"


def test_rule_apply():
    test_word = "d'afgestrede"

