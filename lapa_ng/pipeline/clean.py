import unicodedata

def create_pipeline(*functions: callable) -> callable:
    """
    Combine a list of functions into a single function that applies each function in order.
    """
    def combined_function(text: str) -> str:
        for function in functions:
            text = function(text)
        return text
    return combined_function


def ensure_text(text: str | None) -> str:
    """
    Ensure that the text is a string and not None.
    
    Args:
        text (str | None): Input text that may be None
        
    Returns:
        str: Empty string if input is None, otherwise the input as a string
        
    Examples:
        >>> ensure_text("hello")
        'hello'
        >>> ensure_text(None)
        ''
        >>> ensure_text(123)
        '123'
    """
    if text is None:
        return ""
    return str(text)

def strip_spaces(text: str) -> str:
    """
    Strip whitespace from the beginning and end of the text.
    
    Args:
        text (str): Input text that may have leading or trailing whitespace
        
    Returns:
        str: Text with leading and trailing whitespace removed
        
    Examples:
        >>> strip_spaces("  hello  ")
        'hello'
        >>> strip_spaces("hello world")
        'hello world'
        >>> strip_spaces("")
        ''
    """
    return text.strip()

def to_lowercase(text: str) -> str:
    """
    Convert the text to lowercase.
    
    Args:
        text (str): Input text to convert to lowercase
        
    Returns:
        str: Text converted to lowercase
        
    Examples:
        >>> to_lowercase("Hello World")
        'hello world'
        >>> to_lowercase("PYTHON")
        'python'
        >>> to_lowercase("")
        ''
    """
    return text.lower()

def strip_accents(s: str) -> str:
    """
    Remove diacritical marks (accents) from characters in a string.
    
    Args:
        s (str): Input string that may contain accented characters
        
    Returns:
        str: String with all accents removed
        
    Examples:
        >>> strip_accents("café")
        'cafe'
        >>> strip_accents("naïve")
        'naive'
        >>> strip_accents("résumé")
        'resume'
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')