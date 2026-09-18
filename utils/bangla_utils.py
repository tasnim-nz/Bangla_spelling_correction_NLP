"""
Bangla Text Utilities
Common functions for Bangla text processing
"""

import re
import unicodedata


def normalize_bangla_text(text):
    """
    Normalize Bangla text to NFC form

    Args:
        text (str): Input Bangla text

    Returns:
        str: Normalized text
    """
    return unicodedata.normalize('NFC', text)


def is_bangla_character(char):
    """
    Check if a character is Bangla

    Args:
        char (str): Single character

    Returns:
        bool: True if Bangla character
    """
    # Bangla Unicode range: 0980-09FF
    code_point = ord(char)
    return 0x0980 <= code_point <= 0x09FF


def is_bangla_word(word):
    """
    Check if a word contains only Bangla characters

    Args:
        word (str): Input word

    Returns:
        bool: True if all characters are Bangla
    """
    return all(is_bangla_character(c) or c in [' ', '‍'] for c in word)


def remove_non_bangla(text, keep_punctuation=True):
    """
    Remove non-Bangla characters from text

    Args:
        text (str): Input text
        keep_punctuation (bool): Keep punctuation marks

    Returns:
        str: Cleaned text
    """
    if keep_punctuation:
        # Keep Bangla chars and common punctuation
        pattern = r'[^ঀ-৿\s।,;.!?\-]'
    else:
        # Keep only Bangla chars and spaces
        pattern = r'[^ঀ-৿\s]'

    return re.sub(pattern, '', text)


def tokenize_bangla_words(text):
    """
    Simple word tokenization for Bangla

    Args:
        text (str): Input text

    Returns:
        list: List of words
    """
    # Split on whitespace and punctuation
    words = re.findall(r'[ঀ-৿]+', text)
    return words


def tokenize_bangla_chars(text):
    """
    Character-level tokenization for Bangla

    Args:
        text (str): Input text

    Returns:
        list: List of characters
    """
    return list(text)


# Placeholder for future implementations
def __init__():
    pass
