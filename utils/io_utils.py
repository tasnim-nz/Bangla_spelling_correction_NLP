"""
I/O Utilities for file reading and writing
"""

import json
import pickle
from typing import Any, List, Dict


def read_text_file(filepath: str, encoding='utf-8') -> str:
    """
    Read text file

    Args:
        filepath: Path to file
        encoding: File encoding

    Returns:
        str: File contents
    """
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()


def write_text_file(filepath: str, content: str, encoding='utf-8'):
    """
    Write text file

    Args:
        filepath: Path to file
        content: Text to write
        encoding: File encoding
    """
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(content)


def read_lines(filepath: str, encoding='utf-8') -> List[str]:
    """
    Read file as list of lines

    Args:
        filepath: Path to file
        encoding: File encoding

    Returns:
        list: Lines from file
    """
    with open(filepath, 'r', encoding=encoding) as f:
        return [line.strip() for line in f if line.strip()]


def write_lines(filepath: str, lines: List[str], encoding='utf-8'):
    """
    Write list of lines to file

    Args:
        filepath: Path to file
        lines: List of lines
        encoding: File encoding
    """
    with open(filepath, 'w', encoding=encoding) as f:
        for line in lines:
            f.write(line + '\n')


def read_json(filepath: str) -> Dict:
    """
    Read JSON file

    Args:
        filepath: Path to JSON file

    Returns:
        dict: Parsed JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(filepath: str, data: Dict, indent=4):
    """
    Write JSON file

    Args:
        filepath: Path to JSON file
        data: Data to write
        indent: JSON indentation
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def read_jsonl(filepath: str) -> List[Dict]:
    """
    Read JSONL file (one JSON object per line)

    Args:
        filepath: Path to JSONL file

    Returns:
        list: List of parsed JSON objects
    """
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def write_jsonl(filepath: str, data: List[Dict]):
    """
    Write JSONL file (one JSON object per line)

    Args:
        filepath: Path to JSONL file
        data: List of dictionaries
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def save_pickle(filepath: str, obj: Any):
    """
    Save object using pickle

    Args:
        filepath: Path to pickle file
        obj: Object to save
    """
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)


def load_pickle(filepath: str) -> Any:
    """
    Load object from pickle

    Args:
        filepath: Path to pickle file

    Returns:
        Object loaded from pickle
    """
    with open(filepath, 'rb') as f:
        return pickle.load(f)


# Placeholder for future implementations
def __init__():
    pass
