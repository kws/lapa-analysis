"""
NAF (NLP Annotation Framework) file parsing for LAPA-NG.

This module provides functionality for parsing NAF files and extracting
word forms and their attributes.
"""

from enum import Enum
from typing import Generator
import xml.etree.ElementTree as ET
from dataclasses import dataclass

__all__ = ["parse_naf", "WordForm"]


@dataclass
class WordForm:
    """Represents a word form element from a NAF file.
    
    Attributes:
        text: The text content of the word form
        attributes: Dictionary of XML attributes associated with the word form
    """
    text: str
    attributes: dict[str, str]  

def parse_naf(naf_file: str) -> Generator[WordForm, None, None]:
    """Parse a NAF file and yield WordForm objects.
    
    This function parses a NAF file and yields WordForm objects for each
    word form element found in the text section of the file.
    
    Args:
        naf_file: Path to the NAF file to parse
        
    Yields:
        WordForm objects representing each word form in the file
    """
    is_text_found = False  

    for event, elem in ET.iterparse(naf_file, events=('start', 'end')):

        # Look for the "text" tag to start the parsing of a new text.
        if not is_text_found and event == 'start' and elem.tag == 'text':
            is_text_found = True
            continue

        # When the text tag ends, then we're done
        if is_text_found and event == 'end' and elem.tag == 'text':
            return

        # Found a wf element, yield a WordForm object.
        if is_text_found and event == 'end' and elem.tag == 'wf':
            attribs = dict(elem.attrib)
            text = elem.text
            yield WordForm(text, attribs)

