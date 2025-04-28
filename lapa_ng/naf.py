"""
NAF (NLP Annotation Framework) file parsing for LAPA-NG.

This module provides functionality for parsing NAF files and extracting
word forms and their attributes.
"""

import xml.etree.ElementTree as ET
from typing import Generator

from lapa_ng.types import Word

__all__ = ["parse_naf"]


def parse_naf(naf_file: str) -> Generator[Word, None, None]:
    """Parse a NAF file and yield Word objects.

    This function parses a NAF file and yields WordForm objects for each
    word form element found in the text section of the file.

    Args:
        naf_file: Path to the NAF file to parse

    Yields:
        WordForm objects representing each word form in the file
    """
    is_text_found = False

    for event, elem in ET.iterparse(naf_file, events=("start", "end")):

        # Look for the "text" tag to start the parsing of a new text.
        if not is_text_found and event == "start" and elem.tag == "text":
            is_text_found = True
            continue

        # When the text tag ends, then we're done
        if is_text_found and event == "end" and elem.tag == "text":
            return

        # Found a wf element, yield a WordForm object.
        if is_text_found and event == "end" and elem.tag == "wf":
            attribs = dict(elem.attrib)
            text = elem.text
            yield Word(text, attribs)
