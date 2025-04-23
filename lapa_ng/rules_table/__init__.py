from logging import getLogger
from lapa_ng.rules.matchers import Matcher
from lapa_ng.rules_regex.matching import RegexListMatcher
from lapa_ng.rules_regex.rules import RegexMatcher

from lapa_ng.rules_table.table import check_rules_for_duplicate_priorities, read_excel, read_csv, sort_rules_by_numeric_priority, sort_rules_by_alpha_priority
from lapa_ng.rules_table.regex import rule_to_regex

logger = getLogger(__name__)

__all__ = [
    "load_matchers_from_excel", "sort_rules_by_alpha_priority", "sort_rules_by_numeric_priority", "rule_to_regex", "read_csv", "read_excel"
]


def load_matchers_from_excel(rules_file: str, sheet_name: str | int | None = None, sort_function: callable = sort_rules_by_numeric_priority) -> Matcher:
    """
    Create a translator from a rules file.
    """
    rules = read_excel(rules_file, sheet_name = sheet_name)

    duplicates = check_rules_for_duplicate_priorities(rules)
    for k, v in duplicates.items():
        logger.warning(f"For letter {k[0]} and priority {k[3]} there are {len(v)} duplicates: {', '.join(r.rule_id for r in v)}")

    regex_list = []
    for r in sort_function(rules):
        try:
            regex_list.append(rule_to_regex(r)) 
        except Exception as e:
            print(e)
    
    regex_matchers = [RegexMatcher(r.id, r.pattern, r.replacement, r.meta) for r in regex_list]
    matcher_list = RegexListMatcher(regex_matchers)
    return matcher_list

