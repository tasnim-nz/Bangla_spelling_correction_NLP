"""
Error Patterns for Bangla Spelling Error Generation
Phase 2: Synthetic Error Generation

Defines Bangla-specific error patterns across 5 categories:
  1. Phonetic errors   – Similar-sounding character substitutions
  2. Visual errors     – Similar-looking character substitutions
  3. Typographical      – Insertion / deletion / substitution / transposition
  4. Split-word errors  – Incorrect space insertion within a word
  5. Run-on errors      – Removing space between consecutive words

Each map is bidirectional where applicable.
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    BANGLA_VOWELS, BANGLA_CONSONANTS, BANGLA_DIACRITICS,
    ERROR_TYPES, ERROR_DISTRIBUTION
)

# ============================================================================
# 1. PHONETIC SIMILARITY MAP (expanded)
# ============================================================================
# Characters that sound alike in spoken Bangla.
# Each key maps to a list of phonetically confusable alternatives.

PHONETIC_MAP = {
    # Dental vs Retroflex stops
    'ত': ['ট'],
    'ট': ['ত'],
    'থ': ['ঠ'],
    'ঠ': ['থ'],
    'দ': ['ড'],
    'ড': ['দ'],
    'ধ': ['ঢ'],
    'ঢ': ['ধ'],
    'ন': ['ণ'],
    'ণ': ['ন'],

    # Sibilants
    'শ': ['ষ', 'স'],
    'ষ': ['শ', 'স'],
    'স': ['শ', 'ষ'],

    # Affricates / Nasals
    'জ': ['য'],
    'য': ['জ'],
    'ঞ': ['ন'],

    # Aspirated pairs that get confused in fast speech
    'ক': ['খ'],
    'খ': ['ক'],
    'গ': ['ঘ'],
    'ঘ': ['গ'],
    'চ': ['ছ'],
    'ছ': ['চ'],
    'প': ['ফ'],
    'ফ': ['প'],
    'ব': ['ভ'],
    'ভ': ['ব'],

    # Flap consonants
    'ড়': ['র'],
    'র': ['ড়'],
    'ঢ়': ['ড়'],
}

# ============================================================================
# 2. VISUAL SIMILARITY MAP (expanded)
# ============================================================================
# Characters that look alike in common Bangla fonts.

VISUAL_MAP = {
    'ব': ['ব', 'য়'],
    'য়': ['ব'],
    'ঠ': ['ব'],
    'ক': ['খ'],
    'খ': ['ক'],
    'ত': ['থ'],
    'থ': ['ত'],
    'ড': ['ড়'],
    'ড়': ['ড'],
    'ঢ': ['ঢ়'],
    'ঢ়': ['ঢ'],
    'ঙ': ['ঞ'],
    'ঞ': ['ঙ'],

    # Vowel signs (diacritics) that look similar in small sizes
    'ি': ['ী'],
    'ী': ['ি'],
    'ু': ['ূ'],
    'ূ': ['ু'],
    'ে': ['ৈ'],
    'ৈ': ['ে'],
    'ো': ['ৌ'],
    'ৌ': ['ো'],
}

# ============================================================================
# 3. NEARBY KEYS MAP (for typographical substitution)
# ============================================================================
# Approximation of a standard Bangla (Avro/Probhat) keyboard layout.
# Maps each character to neighbours that could result from a mis-keystroke.

KEYBOARD_NEIGHBOURS = {
    'ক': ['খ', 'গ'],
    'খ': ['ক', 'ঘ'],
    'গ': ['ক', 'ঘ', 'ঙ'],
    'ঘ': ['গ', 'ঙ'],
    'ঙ': ['ঘ'],
    'চ': ['ছ', 'জ'],
    'ছ': ['চ', 'জ'],
    'জ': ['ছ', 'ঝ'],
    'ঝ': ['জ', 'ঞ'],
    'ঞ': ['ঝ'],
    'ট': ['ঠ', 'ড'],
    'ঠ': ['ট', 'ড'],
    'ড': ['ট', 'ঠ', 'ঢ'],
    'ঢ': ['ড', 'ণ'],
    'ণ': ['ঢ', 'ত'],
    'ত': ['ণ', 'থ'],
    'থ': ['ত', 'দ'],
    'দ': ['থ', 'ধ'],
    'ধ': ['দ', 'ন'],
    'ন': ['ধ', 'প'],
    'প': ['ন', 'ফ'],
    'ফ': ['প', 'ব'],
    'ব': ['ফ', 'ভ'],
    'ভ': ['ব', 'ম'],
    'ম': ['ভ', 'য'],
    'য': ['ম', 'র'],
    'র': ['য', 'ল'],
    'ল': ['র', 'শ'],
    'শ': ['ল', 'ষ'],
    'ষ': ['শ', 'স'],
    'স': ['ষ', 'হ'],
    'হ': ['স'],
}

# ============================================================================
# 4. BANGLA CHARACTER POOL (for random insertion / substitution)
# ============================================================================
# Union of vowels, consonants, and common diacritics, used when we need a
# random Bangla character for insertion or wild substitution.

ALL_BANGLA_CHARS = BANGLA_VOWELS + BANGLA_CONSONANTS + BANGLA_DIACRITICS

# ============================================================================
# 5. ERROR WEIGHTS FOR TYPOGRAPHICAL SUB-OPERATIONS
# ============================================================================
# Within the "typographical" category, how we split across sub-operations.

TYPO_SUB_OPERATIONS = {
    'substitution':  0.30,   # Replace a character with a nearby key
    'insertion':     0.25,   # Insert an extra character
    'deletion':      0.25,   # Delete a character
    'transposition': 0.20,   # Swap two adjacent characters
}

# ============================================================================
# 6. ERROR GENERATION CONSTRAINTS
# ============================================================================

MIN_WORD_LENGTH_FOR_ERROR = 3      # Don't corrupt very short words
MAX_ERRORS_PER_SENTENCE = 3        # Cap on number of words modified per sentence
ERROR_RATE_PER_SENTENCE = 0.15     # ~15 % of words in a sentence get an error
MIN_SPLIT_WORD_LENGTH = 5          # Minimum word length to apply a split error
RUN_ON_MAX_WORDS = 2               # How many consecutive words to join


# ============================================================================
# CONVENIENCE HELPERS
# ============================================================================

def get_phonetic_candidates(char):
    """Return list of phonetically similar characters (or empty list)."""
    return PHONETIC_MAP.get(char, [])


def get_visual_candidates(char):
    """Return list of visually similar characters (or empty list)."""
    return VISUAL_MAP.get(char, [])


def get_keyboard_neighbours(char):
    """Return list of nearby-keyboard characters (or empty list)."""
    return KEYBOARD_NEIGHBOURS.get(char, [])


# ============================================================================
# MODULE SELF-TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Error Patterns Module - Self-Test")
    print("=" * 60)

    print(f"\nPhonetic map entries : {len(PHONETIC_MAP)}")
    print(f"Visual map entries   : {len(VISUAL_MAP)}")
    print(f"Keyboard map entries : {len(KEYBOARD_NEIGHBOURS)}")
    print(f"Total Bangla chars   : {len(ALL_BANGLA_CHARS)}")

    print("\nSample phonetic pairs:")
    for ch, alts in list(PHONETIC_MAP.items())[:5]:
        print(f"  {ch} → {alts}")

    print("\nSample visual pairs:")
    for ch, alts in list(VISUAL_MAP.items())[:5]:
        print(f"  {ch} → {alts}")

    print("\nError distribution:")
    for etype, weight in ERROR_DISTRIBUTION.items():
        print(f"  {etype:20s}: {weight:.0%}")

    print("\nTypo sub-operations:")
    for op, w in TYPO_SUB_OPERATIONS.items():
        print(f"  {op:20s}: {w:.0%}")

    print("\n✓ error_patterns.py loaded successfully")
