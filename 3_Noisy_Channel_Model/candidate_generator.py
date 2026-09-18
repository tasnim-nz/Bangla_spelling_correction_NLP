"""Dictionary-filtered Bangla correction candidate generation.

The functions in this module create possible clean words only.  Candidate
ranking and noisy-channel probabilities are intentionally handled elsewhere.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path
from typing import Iterable, Mapping


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESOURCES_DIRECTORY = PROJECT_ROOT / "resources"
DICTIONARY_PATH = RESOURCES_DIRECTORY / "bangla_dictionary.txt"


def _is_bangla_character(character: str) -> bool:
    """Return whether a character is a Bangla letter or combining mark."""
    return (
        len(character) == 1
        and "\u0980" <= character <= "\u09ff"
        and unicodedata.category(character)[0] in {"L", "M"}
    )


def _is_bangla_word(word: str) -> bool:
    """Return whether text is a non-empty Bangla word, not a number/token."""
    return bool(word) and all(_is_bangla_character(character) for character in word)


def _tokenize_bangla_units(word: str) -> list[str]:
    """Group Unicode code points into units without separating conjuncts.

    A virama (্) joins its surrounding consonants into one unit.  Dependent
    vowel signs and other combining marks remain with the base/conjunct they
    modify, so edit operations never create an orphaned conjunct component.
    """
    units: list[str] = []
    current_unit = ""
    join_next_consonant = False

    for character in word:
        if not current_unit:
            current_unit = character
        elif join_next_consonant or unicodedata.category(character).startswith("M"):
            current_unit += character
            join_next_consonant = False
        else:
            units.append(current_unit)
            current_unit = character

        if character == "\u09cd":
            join_next_consonant = True

    if current_unit:
        units.append(current_unit)
    return units


def load_dictionary() -> set[str]:
    """Load the project Bangla dictionary as a UTF-8 set of valid words."""
    with DICTIONARY_PATH.open("r", encoding="utf-8") as dictionary_file:
        return {
            word.strip()
            for word in dictionary_file
            if _is_bangla_word(word.strip())
        }


def _load_mapping(filename: str) -> dict[str, list[str]]:
    """Load one UTF-8 character-confusion mapping from project resources."""
    with (RESOURCES_DIRECTORY / filename).open("r", encoding="utf-8") as map_file:
        return json.load(map_file)


# Load static resources once when the module starts.
DICTIONARY = load_dictionary()
PHONETIC_MAP = _load_mapping("phonetic_map.json")
VISUAL_MAP = _load_mapping("visual_map.json")
KEYBOARD_MAP = _load_mapping("keyboard_map.json")
COMMON_CONJUNCTS = ("ক্ষ", "জ্ঞ", "ত্র", "শ্র")
BANGLA_ALPHABET = tuple(sorted({
    character
    for dictionary_word in DICTIONARY
    for character in dictionary_word
    if _is_bangla_character(character)
} | set(COMMON_CONJUNCTS)))


def _one_edit_variants(word: str) -> Iterable[str]:
    """Yield raw one-unit edit variants in deterministic operation order."""
    units = _tokenize_bangla_units(word)

    # Substitution and deletion at every Unicode/conjunct-safe unit position.
    for index, unit in enumerate(units):
        for replacement in BANGLA_ALPHABET:
            if replacement != unit:
                yield "".join(units[:index] + [replacement] + units[index + 1:])
                # Preserve a vowel sign when replacing a full unit with a
                # consonant conjunct, e.g. খা -> ক্ষা in শিক্ষা.
                vowel_signs = "".join(
                    character
                    for character in unit
                    if "BENGALI VOWEL SIGN" in unicodedata.name(character, "")
                )
                if "\u09cd" in replacement and vowel_signs:
                    yield "".join(
                        units[:index] + [replacement + vowel_signs] + units[index + 1:]
                    )
        yield "".join(units[:index] + units[index + 1:])

    # Insertion can occur before, between, or after existing safe units.
    for index in range(len(units) + 1):
        for insertion in BANGLA_ALPHABET:
            yield "".join(units[:index] + [insertion] + units[index:])

    # Only unequal adjacent units produce a changed transposition.
    for index in range(len(units) - 1):
        if units[index] != units[index + 1]:
            yield "".join(units[:index] + [units[index + 1], units[index]] + units[index + 2:])


def _dictionary_candidates(variants: Iterable[str], original_word: str) -> list[str]:
    """Keep valid dictionary variants once, in the order they are generated."""
    candidates: list[str] = []
    seen: set[str] = set()
    for candidate in variants:
        if (
            candidate != original_word
            and candidate in DICTIONARY
            and candidate not in seen
        ):
            seen.add(candidate)
            candidates.append(candidate)
    return candidates


def edit_distance_one(word: str) -> list[str]:
    """Return dictionary words exactly one insertion, deletion, swap, or substitution away."""
    if not _is_bangla_word(word):
        return []
    return _dictionary_candidates(_one_edit_variants(word), word)


def edit_distance_two(word: str) -> list[str]:
    """Return dictionary words reachable by applying the one-edit operations twice."""
    if not _is_bangla_word(word):
        return []

    candidates: list[str] = []
    seen: set[str] = set()
    # Keep the first stage unfiltered: a genuine two-edit correction can have a
    # non-dictionary intermediate form.  The final candidate is dictionary-only.
    first_edits = dict.fromkeys(_one_edit_variants(word))
    for intermediate_word in first_edits:
        for candidate in _one_edit_variants(intermediate_word):
            if candidate != word and candidate in DICTIONARY and candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)
    return candidates


def map_based_candidates(word: str, mapping: Mapping[str, list[str]]) -> list[str]:
    """Return dictionary words produced by one mapped character replacement."""
    if not _is_bangla_word(word):
        return []

    variants = (
        word[:index] + replacement + word[index + 1:]
        for index, character in enumerate(word)
        for replacement in mapping.get(character, [])
        if replacement != character
    )
    return _dictionary_candidates(variants, word)


def generate_candidates(word: str) -> list[str]:
    """Combine candidate sources, then apply lightweight relevance filtering."""
    if not _is_bangla_word(word):
        return []

    input_characters = {character for character in word if _is_bangla_character(character)}
    candidate_sources = (
        map_based_candidates(word, PHONETIC_MAP),   # 1st priority
        map_based_candidates(word, VISUAL_MAP),     # 2nd priority
        map_based_candidates(word, KEYBOARD_MAP),   # 3rd priority
        edit_distance_one(word),                    # 4th priority
        edit_distance_two(word),                    # 5th priority
    )
    candidates: list[str] = []
    seen: set[str] = set()
    for source in candidate_sources:
        for candidate in source:
            candidate_characters = {
                character for character in candidate if _is_bangla_character(character)
            }
            is_latin_abbreviation = candidate.isascii() and (
                candidate.isupper() or len(candidate) <= 4
            )
            common_chars = len(input_characters & candidate_characters)

            if (
                candidate not in seen
                and candidate != word
                and abs(len(candidate) - len(word)) <= 1
                and common_chars >= max(2, len(input_characters) // 2)
                and not is_latin_abbreviation
            ):
                seen.add(candidate)
                candidates.append(candidate)
    return candidates


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for sample_word in ("বাংলাদেস", "শিখখা", "ভাংলাদেশ", "লাইণে", "তিণি"):
        candidates = generate_candidates(sample_word)
        print(f"Word: {sample_word}")
        print("Candidates:")
        for candidate in candidates:
            print(f"- {candidate}")
        print(f"Total candidate count: {len(candidates)}\n")
