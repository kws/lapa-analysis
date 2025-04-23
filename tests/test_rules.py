import pytest
from lapa_classic.sampify import Sampify

# Here we test the main rule matcher. 
#
# _test_case is called from _test_rule
#
# rule['rule'] is a list of strings that make up the rule.
# wl is the word to be translated, and wl[position:] is the remainder of the word
# tl is the type of letters to be tested, either C, V or S if already translated. 
#
# The loop counts from 0 to the length of the rule. The if just checks if the there are enough letters
# left in the word, and supplies None if there are not. It basically fills the remainder of the word and type arrays with None.
#
# for i in range(len(rule['rule'])):
#     if len(wl[position:]) < i + 1:
#         all_outcomes.append(self._test_case(None, None, rule['rule'][i]))
#     else:
#         all_outcomes.append(self._test_case(wl[position:][i], tl[position:][i], rule['rule'][i]))
# There are four types of rules:
#   * A numeric rule, which can be 1 or 0 indicating the presence of a letter or not.
#   * A single character rule, which just matches that specific character.
#   * A T=c rule which matches if type of the current letter matches the type T and the character is c.
#   * A T=[01] rule which matches if type of the current letter either matches (1) or does not match (0) the type T.


@pytest.fixture
def rules():
    return Sampify()

def test_numeric_rules(rules):

    # Test beyond the end of the word
    assert rules._test_case(tvl=None, tvt=None, r=0) == True
    assert rules._test_case(tvl=None, tvt=None, r=1) == False

    # Test on a part of the word
    assert rules._test_case(tvl='a', tvt='V', r=0) == False
    assert rules._test_case(tvl='a', tvt='V', r=1) == True

def test_single_character_rules(rules):

    # In the real code tvt is generally supplied, but does not take part in the test
    assert rules._test_case(tvl='a', tvt=None, r='a') == True
    assert rules._test_case(tvl='a', tvt=None, r='b') == False

def test_letter_type_rules(rules):

    assert rules._test_case(tvl='a', tvt='V', r='V=a') == True
    assert rules._test_case(tvl='a', tvt='V', r='V=b') == False

    assert rules._test_case(tvl='a', tvt='V', r='C=b') == False

@pytest.mark.skip(reason="This test actually incorrectly returns True")
def test_letter_type_rules_broken(rules):
    assert rules._test_case(tvl='a', tvt='V', r='C=a') == False # THIS TEST ACTUALLY INCORRECTLY RETURNS TRUE WHICH IS WHY WE SKIP IT

def test_type_presence_rules(rules):

    assert rules._test_case(tvl='a', tvt='V', r='V=0') == False
    assert rules._test_case(tvl='a', tvt='V', r='V=1') == True
    assert rules._test_case(tvl='a', tvt='C', r='V=0') == True
    assert rules._test_case(tvl='a', tvt='C', r='V=1') == False

    assert rules._test_case(tvl='b', tvt='V', r='C=0') == True
    assert rules._test_case(tvl='b', tvt='V', r='C=1') == False    
    assert rules._test_case(tvl='b', tvt='C', r='C=0') == False
    assert rules._test_case(tvl='b', tvt='C', r='C=1') == True
