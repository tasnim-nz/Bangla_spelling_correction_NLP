"""
Synthetic Bangla Spelling Error Generator
Phase 2: Error Generation

Takes clean Bangla sentences from Phase 1 and injects realistic spelling
errors to create parallel (erroneous, correct) pairs for training and
evaluation.

Error categories (see error_patterns.py for maps):
  1. Phonetic   – swap with phonetically similar character
  2. Visual     – swap with visually similar character
  3. Typographical – insertion / deletion / substitution / transposition
  4. Split-word – insert a space inside a word
  5. Run-on     – remove a space between two consecutive words

Usage:
    cd Bananriti/2_Error_Generation
    python -X utf8 error_generator.py
"""

import os
import sys
import json
import random
import copy
from collections import Counter

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    BANGLA_VOWELS, BANGLA_CONSONANTS, BANGLA_DIACRITICS,
    ERROR_DISTRIBUTION, PATHS, DATASET_SIZES
)
from error_patterns import (
    PHONETIC_MAP, VISUAL_MAP, KEYBOARD_NEIGHBOURS, ALL_BANGLA_CHARS,
    TYPO_SUB_OPERATIONS,
    MIN_WORD_LENGTH_FOR_ERROR, MAX_ERRORS_PER_SENTENCE,
    ERROR_RATE_PER_SENTENCE, MIN_SPLIT_WORD_LENGTH, RUN_ON_MAX_WORDS,
    get_phonetic_candidates, get_visual_candidates, get_keyboard_neighbours,
)
from utils.bangla_utils import (
    normalize_bangla_text, is_bangla_character, tokenize_bangla_words,
)
from utils.io_utils import read_lines, write_json, write_jsonl

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRAIN_PATH = os.path.join(BASE_DIR, PATHS['corpus'], 'train_corpus.txt')
VAL_PATH   = os.path.join(BASE_DIR, PATHS['corpus'], 'val_corpus.txt')
TEST_PATH  = os.path.join(BASE_DIR, PATHS['corpus'], 'test_corpus.txt')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================================
# ERROR INJECTION FUNCTIONS
# ============================================================================

def apply_phonetic_error(word):
    """
    Replace one character in *word* with a phonetically similar one.
    Returns (corrupted_word, description) or (None, None) if no swap is
    possible.
    """
    positions = []
    for i, ch in enumerate(word):
        if get_phonetic_candidates(ch):
            positions.append(i)
    if not positions:
        return None, None

    pos = random.choice(positions)
    original_char = word[pos]
    replacement = random.choice(get_phonetic_candidates(original_char))
    corrupted = word[:pos] + replacement + word[pos + 1:]
    desc = f"phonetic: '{original_char}'→'{replacement}' at pos {pos}"
    return corrupted, desc


def apply_visual_error(word):
    """Replace one character with a visually similar one."""
    positions = []
    for i, ch in enumerate(word):
        if get_visual_candidates(ch):
            positions.append(i)
    if not positions:
        return None, None

    pos = random.choice(positions)
    original_char = word[pos]
    replacement = random.choice(get_visual_candidates(original_char))
    if replacement == original_char:
        # skip identity mapping (e.g., 'ব' → 'ব')
        alts = [c for c in get_visual_candidates(original_char) if c != original_char]
        if not alts:
            return None, None
        replacement = random.choice(alts)
    corrupted = word[:pos] + replacement + word[pos + 1:]
    desc = f"visual: '{original_char}'→'{replacement}' at pos {pos}"
    return corrupted, desc


def _typo_substitution(word):
    """Substitute one character with a keyboard neighbour."""
    positions = []
    for i, ch in enumerate(word):
        if get_keyboard_neighbours(ch):
            positions.append(i)
    if not positions:
        # fallback: random Bangla char substitution
        bangla_positions = [i for i, ch in enumerate(word) if is_bangla_character(ch)]
        if not bangla_positions:
            return None, None
        pos = random.choice(bangla_positions)
        original_char = word[pos]
        replacement = random.choice(ALL_BANGLA_CHARS)
        while replacement == original_char:
            replacement = random.choice(ALL_BANGLA_CHARS)
        corrupted = word[:pos] + replacement + word[pos + 1:]
        return corrupted, f"typo-sub(random): '{original_char}'→'{replacement}' at pos {pos}"

    pos = random.choice(positions)
    original_char = word[pos]
    replacement = random.choice(get_keyboard_neighbours(original_char))
    corrupted = word[:pos] + replacement + word[pos + 1:]
    return corrupted, f"typo-sub: '{original_char}'→'{replacement}' at pos {pos}"


def _typo_insertion(word):
    """Insert a random Bangla character at a random position."""
    pos = random.randint(0, len(word))
    char = random.choice(ALL_BANGLA_CHARS)
    corrupted = word[:pos] + char + word[pos:]
    return corrupted, f"typo-ins: '{char}' at pos {pos}"


def _typo_deletion(word):
    """Delete one character from the word."""
    if len(word) <= 2:
        return None, None
    pos = random.randint(0, len(word) - 1)
    deleted_char = word[pos]
    corrupted = word[:pos] + word[pos + 1:]
    return corrupted, f"typo-del: '{deleted_char}' at pos {pos}"


def _typo_transposition(word):
    """Swap two adjacent characters."""
    if len(word) < 2:
        return None, None
    pos = random.randint(0, len(word) - 2)
    chars = list(word)
    chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
    corrupted = ''.join(chars)
    if corrupted == word:
        return None, None
    return corrupted, f"typo-trans: pos {pos}↔{pos + 1}"


def apply_typographical_error(word):
    """
    Apply one of: substitution / insertion / deletion / transposition,
    chosen by TYPO_SUB_OPERATIONS weights.
    """
    ops = list(TYPO_SUB_OPERATIONS.keys())
    weights = list(TYPO_SUB_OPERATIONS.values())
    chosen_op = random.choices(ops, weights=weights, k=1)[0]

    dispatch = {
        'substitution':  _typo_substitution,
        'insertion':     _typo_insertion,
        'deletion':      _typo_deletion,
        'transposition': _typo_transposition,
    }
    return dispatch[chosen_op](word)


def apply_split_word_error(word):
    """
    Insert a space into the middle of a word (split-word error).
    Only applies to words of sufficient length.
    """
    if len(word) < MIN_SPLIT_WORD_LENGTH:
        return None, None
    # Choose a split point (not at the edges)
    pos = random.randint(2, len(word) - 2)
    corrupted = word[:pos] + ' ' + word[pos:]
    return corrupted, f"split: at pos {pos} → '{word[:pos]}' + '{word[pos:]}'"


# ============================================================================
# SENTENCE-LEVEL ERROR INJECTION
# ============================================================================

def choose_error_type():
    """Pick an error type according to the configured distribution."""
    types = list(ERROR_DISTRIBUTION.keys())
    weights = list(ERROR_DISTRIBUTION.values())
    return random.choices(types, weights=weights, k=1)[0]


def inject_errors_into_sentence(sentence):
    """
    Inject spelling errors into a clean Bangla sentence.

    Returns:
        dict with keys:
            original   – the clean sentence
            corrupted  – the erroneous sentence
            errors     – list of {word_index, original_word, corrupted_word,
                         error_type, description}
    """
    words = sentence.split()
    if len(words) < 3:
        return None   # too short to meaningfully corrupt

    num_errors = max(1, min(
        MAX_ERRORS_PER_SENTENCE,
        round(len(words) * ERROR_RATE_PER_SENTENCE)
    ))

    # Gather candidate positions (word indices eligible for error)
    candidates = [
        i for i, w in enumerate(words)
        if len(w) >= MIN_WORD_LENGTH_FOR_ERROR and is_valid_bangla_word(w)
    ]
    if not candidates:
        return None

    random.shuffle(candidates)
    chosen_indices = candidates[:num_errors]

    corrupted_words = list(words)
    error_records = []
    used_indices = set()

    for idx in chosen_indices:
        error_type = choose_error_type()

        # Handle split-word and run-on specially (they change sentence structure)
        if error_type == 'run_on':
            # Join this word with the next one (if possible)
            if idx + 1 < len(corrupted_words) and idx + 1 not in used_indices:
                original_pair = corrupted_words[idx] + ' ' + corrupted_words[idx + 1]
                merged = corrupted_words[idx] + corrupted_words[idx + 1]
                corrupted_words[idx] = merged
                corrupted_words[idx + 1] = ''  # mark for removal later
                used_indices.add(idx)
                used_indices.add(idx + 1)
                error_records.append({
                    'word_index': idx,
                    'original_word': original_pair,
                    'corrupted_word': merged,
                    'error_type': 'run_on',
                    'description': f"run-on: merged words at pos {idx} and {idx + 1}",
                })
                continue
            else:
                error_type = 'typographical'  # fallback

        if error_type == 'split_word':
            result, desc = apply_split_word_error(corrupted_words[idx])
            if result is None:
                error_type = 'typographical'  # fallback
            else:
                original_word = corrupted_words[idx]
                corrupted_words[idx] = result
                used_indices.add(idx)
                error_records.append({
                    'word_index': idx,
                    'original_word': original_word,
                    'corrupted_word': result,
                    'error_type': 'split_word',
                    'description': desc,
                })
                continue

        # Word-level error (phonetic, visual, typographical)
        word = corrupted_words[idx]

        if error_type == 'phonetic':
            result, desc = apply_phonetic_error(word)
        elif error_type == 'visual':
            result, desc = apply_visual_error(word)
        else:
            result, desc = apply_typographical_error(word)

        if result is None or result == word:
            # Fallback to generic typographical if first attempt fails
            result, desc = apply_typographical_error(word)

        if result is not None and result != word:
            original_word = words[idx]  # use the original (pre-corruption) word
            corrupted_words[idx] = result
            used_indices.add(idx)
            error_records.append({
                'word_index': idx,
                'original_word': original_word,
                'corrupted_word': result,
                'error_type': error_type,
                'description': desc,
            })

    if not error_records:
        return None

    # Reassemble sentence (filter out empty tokens from run-on merges)
    corrupted_sentence = ' '.join(w for w in corrupted_words if w)

    return {
        'original': sentence,
        'corrupted': corrupted_sentence,
        'errors': error_records,
    }


def is_valid_bangla_word(word):
    """Check that a word contains at least one Bangla character."""
    return any(is_bangla_character(ch) for ch in word)


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def generate_error_corpus(sentences, error_variants_per_sentence=2):
    """
    Generate synthetic error pairs from a list of clean sentences.

    Each clean sentence produces up to *error_variants_per_sentence*
    different erroneous versions (to increase data volume).

    Returns:
        list of dicts – each with original, corrupted, errors
    """
    all_pairs = []
    skipped = 0

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        for _ in range(error_variants_per_sentence):
            result = inject_errors_into_sentence(sent)
            if result is not None:
                all_pairs.append(result)
            else:
                skipped += 1

    return all_pairs, skipped


# ============================================================================
# STATISTICS
# ============================================================================

def compute_statistics(pairs):
    """Compute summary statistics for the generated error corpus."""
    error_type_counter = Counter()
    total_errors = 0
    errors_per_sentence = []

    for pair in pairs:
        n = len(pair['errors'])
        errors_per_sentence.append(n)
        total_errors += n
        for err in pair['errors']:
            error_type_counter[err['error_type']] += 1

    stats = {
        'total_pairs': len(pairs),
        'total_errors_injected': total_errors,
        'avg_errors_per_sentence': round(total_errors / max(len(pairs), 1), 2),
        'error_type_distribution': dict(error_type_counter),
        'error_type_percentages': {
            k: round(v / max(total_errors, 1) * 100, 1)
            for k, v in error_type_counter.items()
        },
        'max_errors_in_one_sentence': max(errors_per_sentence, default=0),
        'min_errors_in_one_sentence': min(errors_per_sentence, default=0),
    }
    return stats


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 65)
    print("  Phase 2: Synthetic Bangla Spelling Error Generation")
    print("  বানানরীতি (Bananriti)")
    print("=" * 65)

    # ---- Load clean corpora ------------------------------------------------
    print("\n[1/4] Loading clean corpora ...")
    train_sentences = read_lines(TRAIN_PATH)
    val_sentences   = read_lines(VAL_PATH)
    test_sentences  = read_lines(TEST_PATH)

    print(f"  Train sentences : {len(train_sentences)}")
    print(f"  Val sentences   : {len(val_sentences)}")
    print(f"  Test sentences  : {len(test_sentences)}")

    # ---- Generate errors ---------------------------------------------------
    print("\n[2/4] Generating synthetic errors ...")

    # Train: 2 error variants per sentence → ~274 pairs
    train_pairs, train_skipped = generate_error_corpus(
        train_sentences, error_variants_per_sentence=2
    )
    # Validation: 1 variant per sentence
    val_pairs, val_skipped = generate_error_corpus(
        val_sentences, error_variants_per_sentence=1
    )
    # Test: 1 variant per sentence
    test_pairs, test_skipped = generate_error_corpus(
        test_sentences, error_variants_per_sentence=1
    )

    print(f"  Train pairs generated : {len(train_pairs)}  (skipped: {train_skipped})")
    print(f"  Val pairs generated   : {len(val_pairs)}  (skipped: {val_skipped})")
    print(f"  Test pairs generated  : {len(test_pairs)}  (skipped: {test_skipped})")

    # ---- Save outputs ------------------------------------------------------
    print("\n[3/4] Saving output files ...")

    # Detailed JSONL (all fields)
    write_jsonl(os.path.join(OUTPUT_DIR, 'train_errors.jsonl'), train_pairs)
    write_jsonl(os.path.join(OUTPUT_DIR, 'val_errors.jsonl'),   val_pairs)
    write_jsonl(os.path.join(OUTPUT_DIR, 'test_errors.jsonl'),  test_pairs)
    print("  ✓ train_errors.jsonl")
    print("  ✓ val_errors.jsonl")
    print("  ✓ test_errors.jsonl")

    # Simple parallel TSV (corrupted <TAB> correct) – easy to eyeball
    for name, pairs in [('train', train_pairs), ('val', val_pairs), ('test', test_pairs)]:
        tsv_path = os.path.join(OUTPUT_DIR, f'{name}_parallel.tsv')
        with open(tsv_path, 'w', encoding='utf-8') as f:
            f.write("corrupted\tcorrect\n")
            for p in pairs:
                f.write(f"{p['corrupted']}\t{p['original']}\n")
        print(f"  ✓ {name}_parallel.tsv")

    # ---- Statistics --------------------------------------------------------
    print("\n[4/4] Computing statistics ...")
    all_pairs = train_pairs + val_pairs + test_pairs
    stats = compute_statistics(all_pairs)

    stats['split'] = {
        'train': len(train_pairs),
        'val':   len(val_pairs),
        'test':  len(test_pairs),
    }
    stats['seed'] = SEED

    write_json(os.path.join(OUTPUT_DIR, 'error_generation_stats.json'), stats)
    print("  ✓ error_generation_stats.json")

    # ---- Print summary -----------------------------------------------------
    print("\n" + "=" * 65)
    print("  PHASE 2 SUMMARY")
    print("=" * 65)
    print(f"  Total parallel pairs : {stats['total_pairs']}")
    print(f"  Total errors injected: {stats['total_errors_injected']}")
    print(f"  Avg errors/sentence  : {stats['avg_errors_per_sentence']}")
    print()
    print("  Error type distribution:")
    for etype, count in stats['error_type_distribution'].items():
        pct = stats['error_type_percentages'][etype]
        print(f"    {etype:20s}: {count:4d} ({pct:.1f}%)")

    print()
    print("  Split sizes:")
    for split, count in stats['split'].items():
        print(f"    {split:10s}: {count}")

    # ---- Show sample pairs -------------------------------------------------
    print("\n" + "-" * 65)
    print("  SAMPLE ERROR PAIRS (first 5 from train)")
    print("-" * 65)
    for i, pair in enumerate(train_pairs[:5]):
        print(f"\n  Example {i + 1}:")
        print(f"    Original : {pair['original'][:100]}")
        print(f"    Corrupted: {pair['corrupted'][:100]}")
        for err in pair['errors']:
            print(f"    → [{err['error_type']}] {err['description']}")

    print("\n" + "=" * 65)
    print("  ✓ Phase 2 Complete!")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 65)


if __name__ == '__main__':
    main()
