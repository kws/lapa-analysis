from lapa_ng.table_rules import RuleClass, TabularRule, table_rule_to_regex_spec
from lapa_ng.table_rules._expressions import parse_expression


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

    spec = table_rule_to_regex_spec(tabular_rule)
    assert spec.pattern == "^(a)[:consonant:][:vowel:]"


def test_parse_rule():
    parse_expression("a") == "a"
    parse_expression("1") == "."
    parse_expression("0") == "$"
    parse_expression("C=b") == "b"
    parse_expression("V=b") == "b"
    parse_expression("V=0") == "[bcdfghjklmnpqrstvwxyz]"
    parse_expression("V=1") == "[aeiou]"
    parse_expression("C=0") == "[aeiou]"
    parse_expression("C=1") == "[bcdfghjklmnpqrstvwxyz]"


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

    spec = table_rule_to_regex_spec(tabular_rule)
    assert spec.pattern == "^(abc)$"

    tabular_rule.rule = '["a", "C=b", "C=c", 1]'
    spec = table_rule_to_regex_spec(tabular_rule)
    assert spec.pattern == "^(abc)."

    tabular_rule.rule = '["a", "C=b", "C=c"]'
    spec = table_rule_to_regex_spec(tabular_rule)
    assert spec.pattern == "^(abc)"
