"""Reusable Bangla spelling-error patterns.

This module deliberately contains only sentence-level error logic. The three
character-confusion maps are loaded once at import time; dataset generation and
file handling belong elsewhere in the project.
"""

from __future__ import annotations

import json
import random
import sys
import unicodedata
from pathlib import Path
from typing import Mapping, Sequence


_RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resources"


def _load_map(filename: str) -> dict[str, list[str]]:
    """Load one project character-confusion map as UTF-8 JSON."""
    with (_RESOURCE_DIR / filename).open(encoding="utf-8") as resource_file:
        return json.load(resource_file)


# Resources are loaded once, rather than on every generated error.
PHONETIC_MAP = _load_map("phonetic_map.json")
VISUAL_MAP = _load_map("visual_map.json")
KEYBOARD_MAP = _load_map("keyboard_map.json")


def is_bangla_character(character: str) -> bool:
    """Return whether *character* is a Bangla letter or combining sign.

    Bangla digits and punctuation are excluded so they cannot be split, merged,
    or used as replacement positions.
    """
    return (
        len(character) == 1
        and "\u0980" <= character <= "\u09ff"
        and unicodedata.category(character)[0] in {"L", "M"}
    )


def _is_bangla_word(text: str) -> bool:
    """Return whether text consists solely of Bangla letters/signs."""
    return bool(text) and all(is_bangla_character(character) for character in text)


def _replace_one_mapped_character(
    sentence: str, character_map: Mapping[str, Sequence[str]]
) -> str:
    """Replace one randomly selected position having a usable mapped value."""
    candidates = []
    for index, character in enumerate(sentence):
        replacements = [
            replacement
            for replacement in character_map.get(character, [])
            if replacement != character
        ]
        if is_bangla_character(character) and replacements:
            candidates.append((index, replacements))

    if not candidates:
        return sentence

    index, replacements = random.choice(candidates)
    replacement = random.choice(replacements)
    return sentence[:index] + replacement + sentence[index + 1:]


def phonetic_error(sentence: str) -> str:
    """Make exactly one phonetic Bangla-character substitution, if possible."""
    return _replace_one_mapped_character(sentence, PHONETIC_MAP)


def visual_error(sentence: str) -> str:
    """Make exactly one visually similar Bangla-character substitution."""
    return _replace_one_mapped_character(sentence, VISUAL_MAP)


def keyboard_error(sentence: str) -> str:
    """Make exactly one nearby-key keyboard character/vowel-sign substitution."""
    return _replace_one_mapped_character(sentence, KEYBOARD_MAP)


def _word_spans(sentence: str) -> list[tuple[int, int]]:
    """Find contiguous Bangla words without treating punctuation as a word."""
    spans: list[tuple[int, int]] = []
    start: int | None = None
    for index, character in enumerate(sentence):
        if is_bangla_character(character):
            if start is None:
                start = index
        elif start is not None:
            spans.append((start, index))
            start = None
    if start is not None:
        spans.append((start, len(sentence)))
    return spans


def _valid_split_positions(word: str) -> list[int]:
    """Return internal boundaries that do not separate a combining sequence."""
    positions = []
    for position in range(1, len(word)):
        previous, following = word[position - 1], word[position]
        # A vowel sign/other mark belongs to the preceding base letter. A
        # virama (্) also must remain attached to the character before it.
        if unicodedata.category(following).startswith("M") or previous == "\u09cd":
            continue
        positions.append(position)
    return positions


def split_word_error(sentence: str) -> str:
    """Split one long Bangla word at a conservative morpheme/syllable boundary.

    A random character boundary can break a conjunct or create implausible word
    fragments.  Prefer familiar productive word-initial morphemes; otherwise,
    permit only a boundary immediately after a Bangla vowel sign.  Both choices
    are additionally checked to ensure no combining sequence is separated.
    """
    common_initial_morphemes = (
        "বাংলা", "বিশ্ব", "শিক্ষা", "রাষ্ট্র", "দেশ", "বিদ্যা", "প্রতি",
        "পরি", "সমাজ", "সরকার", "কর্ম", "জন", "আন্তর", "উপ",
    )
    candidates: list[tuple[int, list[int]]] = []

    for start, end in _word_spans(sentence):
        word = sentence[start:end]
        if not _is_bangla_word(word) or len(word) < 5:
            continue

        safe_positions = set(_valid_split_positions(word))
        morpheme_positions = [
            len(morpheme)
            for morpheme in common_initial_morphemes
            if word.startswith(morpheme) and len(morpheme) in safe_positions
        ]

        # A vowel sign completes the preceding syllable, making the following
        # base letter a conservative fallback split point.
        syllable_positions = [
            position
            for position in safe_positions
            if "BENGALI VOWEL SIGN" in unicodedata.name(word[position - 1], "")
        ]
        positions = morpheme_positions or syllable_positions
        if positions:
            candidates.append((start, positions))

    if not candidates:
        return sentence

    start, positions = random.choice(candidates)
    position = random.choice(positions)
    return sentence[:start + position] + " " + sentence[start + position:]


def run_on_error(sentence: str) -> str:
    """Merge one eligible adjacent Bangla-word pair by removing one space."""
    blocked_first_words = {
        "করে", "করা", "হয়", "হবে", "ছিল", "ছিলেন", "আছে", "থেকে",
        "সঙ্গে", "যায়", "দিয়ে", "নিয়ে",
    }
    candidates: list[tuple[int, int]] = []
    spans = _word_spans(sentence)
    for (left_start, left_end), (right_start, right_end) in zip(spans, spans[1:]):
        first_word = sentence[left_start:left_end]
        second_word = sentence[right_start:right_end]
        separator = sentence[left_end:right_start]
        first_letter_count = sum(
            unicodedata.category(character).startswith("L") for character in first_word
        )
        second_letter_count = sum(
            unicodedata.category(character).startswith("L") for character in second_word
        )
        # A literal one-space separator ensures punctuation, tabs, and repeated
        # whitespace cannot be consumed by the run-on transformation.
        if (
            separator == " "
            and first_word not in blocked_first_words
            and first_letter_count >= 2
            and second_letter_count >= 2
        ):
            candidates.append((left_end, right_start))

    if not candidates:
        return sentence

    left_end, right_start = random.choice(candidates)
    return sentence[:left_end] + sentence[right_start:]


def apply_error(sentence: str, error_type: str) -> str:
    """Apply one named error pattern, or return the input for an unknown type."""
    error_functions = {
        "phonetic": phonetic_error,
        "visual": visual_error,
        "keyboard": keyboard_error,
        "split": split_word_error,
        "run_on": run_on_error,
    }
    error_function = error_functions.get(error_type)
    return error_function(sentence) if error_function else sentence


if __name__ == "__main__":
    # Make the demonstration reliable when launched from legacy Windows shells.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sample_sentence = "শিক্ষার্থীরা আজ বাংলাদেশে এসেছে।"
    print(f"Phonetic : {phonetic_error(sample_sentence)}")
    print(f"Visual : {visual_error(sample_sentence)}")
    print(f"Keyboard : {keyboard_error(sample_sentence)}")
    print(f"Split : {split_word_error(sample_sentence)}")
    print(f"Run-on : {run_on_error(sample_sentence)}")
