"""
Phase 1: Data Preprocessing - Step 2
Split corpus into train/validation/test sets

This script:
1. Loads clean corpus
2. Shuffles sentences
3. Splits into train (70%), validation (10%), test (20%)
4. Saves each split separately
5. Generates split statistics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from utils.io_utils import read_lines, write_lines, write_json
from utils.bangla_utils import tokenize_bangla_words


def split_corpus(clean_corpus_file, output_dir, train_ratio=0.7, val_ratio=0.1, test_ratio=0.2, seed=42):
    """
    Split corpus into train/val/test sets

    Args:
        clean_corpus_file (str): Path to clean corpus
        output_dir (str): Output directory
        train_ratio (float): Training set ratio
        val_ratio (float): Validation set ratio
        test_ratio (float): Test set ratio
        seed (int): Random seed for reproducibility
    """
    print("\n" + "="*70)
    print("PHASE 1: CORPUS SPLITTING")
    print("="*70)

    # Validate ratios
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, "Ratios must sum to 1.0"

    # Step 1: Load clean corpus
    print("\n[1/5] Loading clean corpus...")
    sentences = read_lines(clean_corpus_file)
    print(f"✓ Loaded {len(sentences)} sentences")

    # Step 2: Shuffle sentences
    print("\n[2/5] Shuffling sentences...")
    random.seed(seed)
    random.shuffle(sentences)
    print(f"✓ Sentences shuffled (seed={seed})")

    # Step 3: Calculate split sizes
    print("\n[3/5] Calculating split sizes...")
    total = len(sentences)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)
    test_size = total - train_size - val_size  # Remaining goes to test

    print(f"✓ Train: {train_size} sentences ({train_ratio*100:.0f}%)")
    print(f"✓ Validation: {val_size} sentences ({val_ratio*100:.0f}%)")
    print(f"✓ Test: {test_size} sentences ({test_ratio*100:.0f}%)")

    # Step 4: Split data
    print("\n[4/5] Creating splits...")
    train_data = sentences[:train_size]
    val_data = sentences[train_size:train_size + val_size]
    test_data = sentences[train_size + val_size:]

    # Verify split
    assert len(train_data) + len(val_data) + len(test_data) == total
    print(f"✓ Split verification passed")

    # Step 5: Save splits
    print("\n[5/5] Saving splits...")
    os.makedirs(output_dir, exist_ok=True)

    # Save train set
    train_file = os.path.join(output_dir, "train_corpus.txt")
    write_lines(train_file, train_data)
    print(f"✓ Saved: {train_file}")

    # Save validation set
    val_file = os.path.join(output_dir, "val_corpus.txt")
    write_lines(val_file, val_data)
    print(f"✓ Saved: {val_file}")

    # Save test set
    test_file = os.path.join(output_dir, "test_corpus.txt")
    write_lines(test_file, test_data)
    print(f"✓ Saved: {test_file}")

    # Calculate statistics for each split
    print("\n" + "-"*70)
    print("SPLIT STATISTICS")
    print("-"*70)

    splits = {
        "train": train_data,
        "validation": val_data,
        "test": test_data
    }

    split_stats = {}

    for split_name, split_data in splits.items():
        total_words = sum(len(tokenize_bangla_words(s)) for s in split_data)
        avg_words = total_words / len(split_data) if split_data else 0

        stats = {
            "sentences": len(split_data),
            "total_words": total_words,
            "avg_words_per_sentence": round(avg_words, 2)
        }

        split_stats[split_name] = stats

        print(f"\n{split_name.upper()}:")
        print(f"  Sentences: {stats['sentences']:,}")
        print(f"  Total words: {stats['total_words']:,}")
        print(f"  Avg words/sentence: {stats['avg_words_per_sentence']}")

    # Save split statistics
    stats_file = os.path.join(output_dir, "split_stats.json")
    split_info = {
        "total_sentences": total,
        "train_ratio": train_ratio,
        "val_ratio": val_ratio,
        "test_ratio": test_ratio,
        "random_seed": seed,
        "splits": split_stats
    }
    write_json(stats_file, split_info)
    print(f"\n✓ Saved statistics: {stats_file}")

    print("\n" + "="*70)
    print("✓ CORPUS SPLITTING COMPLETE")
    print("="*70)
    print(f"\nData split into:")
    print(f"  • Train: {train_size} sentences")
    print(f"  • Validation: {val_size} sentences")
    print(f"  • Test: {test_size} sentences")
    print(f"\nReady for language model training\n")

    return train_data, val_data, test_data, split_stats


if __name__ == "__main__":
    # Paths
    clean_corpus_file = "outputs/clean_corpus.txt"
    output_dir = "outputs"

    # Check if clean corpus exists
    if not os.path.exists(clean_corpus_file):
        print("ERROR: clean_corpus.txt not found!")
        print("Please run preprocess.py first")
        sys.exit(1)

    # Split corpus
    train_data, val_data, test_data, stats = split_corpus(
        clean_corpus_file,
        output_dir,
        train_ratio=0.7,
        val_ratio=0.1,
        test_ratio=0.2,
        seed=42
    )

    print("Next step: Run build_language_model.py to train n-gram LM")
