from enum import Enum
from typing import Generator
import xml.etree.ElementTree as ET
from dataclasses import dataclass

__all__ = ["parse_naf", "WordForm"]


@dataclass
class WordForm:
    """
    Represents a wf element in a NAF file.

    :param text: The text of the word form.
    :type text: str

    :param attributes: The attributes of the word form.
    :type attributes: dict[str, str]
    """
    text: str
    attributes: dict[str, str]  

def parse_naf(naf_file: str) -> Generator[WordForm, None, None]:
    """
    Parse a NAF file and yield WordForm objects.

    :param naf_file: The path to the NAF file to parse.
    :type naf_file: str

    :return: A generator of WordForm objects.
    :rtype: Generator[WordForm, None, None]
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

