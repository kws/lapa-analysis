from lapa_ng.factory import parse_matcher_spec


def test_parse_basic():
    spec = parse_matcher_spec("ng:rules.xlsx")

    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == None
    assert spec.options == None


def test_parse_with_section():
    spec = parse_matcher_spec("ng:rules.xlsx#SHEET")

    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == "SHEET"
    assert spec.options == None


def test_parse_with_options():
    spec = parse_matcher_spec("ng:rules.xlsx?OPTIONS")

    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == None
    assert spec.options == "?OPTIONS"


def test_parse_with_section_and_options():
    spec = parse_matcher_spec("ng:rules.xlsx#SHEET?OPTIONS")

    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == "SHEET"
    assert spec.options == "?OPTIONS"


def test_parse_with_section_and_querystring_syntax():
    spec = parse_matcher_spec("ng:rules.xlsx#SHEET?one=1&two=2")

    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == "SHEET"
    assert spec.options == "?one=1&two=2"

    assert spec.qs == {"one": ["1"], "two": ["2"]}
    assert spec.qs_flat == {"one": "1", "two": "2"}


def test_parse_without_prefix():

    spec = parse_matcher_spec("rules.xlsx")
    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == None
    assert spec.options == None

    spec = parse_matcher_spec("rules.xlsx#SHEET?OPTIONS")
    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == "SHEET"
    assert spec.options == "?OPTIONS"

    spec = parse_matcher_spec("rules.xlsx?OPTIONS")
    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == None
    assert spec.options == "?OPTIONS"

    spec = parse_matcher_spec("rules.xlsx#SHEET")
    assert spec.prefix == "ng"
    assert spec.filename == "rules.xlsx"
    assert spec.section == "SHEET"
    assert spec.options == None
