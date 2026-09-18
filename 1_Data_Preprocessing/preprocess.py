"""
Phase 1: Data Preprocessing - Step 1
Preprocess and clean Bangla corpus

This script:
1. Loads raw Bangla corpus
2. Normalizes Unicode to NFC form
3. Cleans text (removes HTML, special chars)
4. Sentence segmentation
5. Tokenization
6. Removes duplicates and malformed sentences
7. Saves clean corpus
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import unicodedata
from collections import Counter
from utils.bangla_utils import (
    normalize_bangla_text,
    is_bangla_word,
    remove_non_bangla,
    tokenize_bangla_words
)
from utils.io_utils import read_text_file, write_lines, write_json


def clean_bangla_sentence(sentence):
    """
    Clean a single Bangla sentence

    Args:
        sentence (str): Raw sentence

    Returns:
        str: Cleaned sentence or None if invalid
    """
    # Remove leading/trailing whitespace
    sentence = sentence.strip()

    # Skip empty sentences
    if not sentence:
        return None

    # Normalize Unicode to NFC form
    sentence = normalize_bangla_text(sentence)

    # Remove HTML tags if present
    sentence = re.sub(r'<[^>]+>', '', sentence)

    # Remove URLs
    sentence = re.sub(r'http[s]?://\S+', '', sentence)

    # Remove extra whitespace
    sentence = re.sub(r'\s+', ' ', sentence).strip()

    # Keep only Bangla characters and basic punctuation
    # Allowed: Bangla chars (0980-09FF), spaces, । , ; . ! ? -
    sentence = re.sub(r'[^ঀ-৿\s।,;.!?\-]', '', sentence)

    # Remove sentences that are too short (< 5 words)
    words = tokenize_bangla_words(sentence)
    if len(words) < 5:
        return None

    # Remove sentences that are too long (> 150 words)
    if len(words) > 150:
        return None

    # Check if sentence has reasonable Bangla content
    bangla_word_count = sum(1 for word in words if is_bangla_word(word))
    if bangla_word_count < 3:  # At least 3 Bangla words
        return None

    return sentence


def split_into_sentences(text):
    """
    Split text into sentences using Bangla punctuation

    Args:
        text (str): Input text

    Returns:
        list: List of sentences
    """
    # Split on Bangla and English sentence terminators
    # । is Bangla full stop (danda)
    sentences = re.split(r'[।\.\!\?]+', text)

    # Clean and filter
    cleaned = []
    for sent in sentences:
        sent = sent.strip()
        if sent:
            cleaned.append(sent)

    return cleaned


def preprocess_corpus(input_file, output_dir):
    """
    Main preprocessing function

    Args:
        input_file (str): Path to raw corpus
        output_dir (str): Output directory
    """
    print("\n" + "="*70)
    print("PHASE 1: DATA PREPROCESSING - BANGLA CORPUS")
    print("="*70)

    # Step 1: Load raw corpus
    print("\n[1/7] Loading raw corpus...")
    raw_text = read_text_file(input_file)
    print(f"✓ Loaded {len(raw_text)} characters")
    print(f"✓ File size: {len(raw_text.encode('utf-8')) / 1024:.2f} KB")

    # Step 2: Split into sentences
    print("\n[2/7] Splitting into sentences...")
    sentences = split_into_sentences(raw_text)
    print(f"✓ Found {len(sentences)} raw sentences")

    # Step 3: Clean sentences
    print("\n[3/7] Cleaning sentences...")
    cleaned_sentences = []
    for i, sent in enumerate(sentences):
        cleaned = clean_bangla_sentence(sent)
        if cleaned:
            cleaned_sentences.append(cleaned)

    print(f"✓ {len(cleaned_sentences)} sentences after cleaning")
    print(f"✓ Removed {len(sentences) - len(cleaned_sentences)} invalid sentences")

    # Step 4: Remove duplicates
    print("\n[4/7] Removing duplicates...")
    unique_sentences = list(set(cleaned_sentences))
    duplicates_removed = len(cleaned_sentences) - len(unique_sentences)
    print(f"✓ {len(unique_sentences)} unique sentences")
    print(f"✓ Removed {duplicates_removed} duplicates")

    # Step 5: Sort by length for better organization
    print("\n[5/7] Organizing sentences...")
    unique_sentences.sort(key=len)

    # Step 6: Calculate statistics
    print("\n[6/7] Calculating statistics...")
    total_words = 0
    total_chars = 0
    word_freq = Counter()

    for sent in unique_sentences:
        words = tokenize_bangla_words(sent)
        total_words += len(words)
        total_chars += len(sent)
        word_freq.update(words)

    avg_words = total_words / len(unique_sentences) if unique_sentences else 0
    avg_chars = total_chars / len(unique_sentences) if unique_sentences else 0
    vocab_size = len(word_freq)

    stats = {
        "total_sentences": len(unique_sentences),
        "total_words": total_words,
        "total_characters": total_chars,
        "vocabulary_size": vocab_size,
        "avg_words_per_sentence": round(avg_words, 2),
        "avg_chars_per_sentence": round(avg_chars, 2),
        "min_words": min(len(tokenize_bangla_words(s)) for s in unique_sentences) if unique_sentences else 0,
        "max_words": max(len(tokenize_bangla_words(s)) for s in unique_sentences) if unique_sentences else 0,
        "duplicates_removed": duplicates_removed,
        "invalid_sentences_removed": len(sentences) - len(cleaned_sentences)
    }

    print(f"✓ Total sentences: {stats['total_sentences']}")
    print(f"✓ Total words: {stats['total_words']:,}")
    print(f"✓ Vocabulary size: {stats['vocabulary_size']:,}")
    print(f"✓ Avg words/sentence: {stats['avg_words_per_sentence']}")

    # Step 7: Save outputs
    print("\n[7/7] Saving outputs...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save cleaned corpus
    corpus_file = os.path.join(output_dir, "clean_corpus.txt")
    write_lines(corpus_file, unique_sentences)
    print(f"✓ Saved clean corpus: {corpus_file}")

    # Save statistics
    stats_file = os.path.join(output_dir, "preprocessing_stats.json")
    write_json(stats_file, stats)
    print(f"✓ Saved statistics: {stats_file}")

    # Save vocabulary with frequencies
    vocab_file = os.path.join(output_dir, "vocabulary.json")
    vocab_dict = {word: count for word, count in word_freq.most_common()}
    write_json(vocab_file, vocab_dict)
    print(f"✓ Saved vocabulary: {vocab_file}")

    # Save top 100 most common words
    print("\n" + "-"*70)
    print("Top 20 Most Common Words:")
    print("-"*70)
    for i, (word, count) in enumerate(word_freq.most_common(20), 1):
        print(f"{i:2}. {word:15} - {count:4} occurrences")

    print("\n" + "="*70)
    print("✓ PREPROCESSING COMPLETE")
    print("="*70)
    print(f"\nClean corpus saved with {len(unique_sentences)} sentences")
    print(f"Ready for train/validation/test split in next step\n")

    return unique_sentences, stats


if __name__ == "__main__":
    # Paths
    input_file = "../../raw_corpus.txt"  # Adjust path if needed
    output_dir = "outputs"

    # Check if input file exists
    if not os.path.exists(input_file):
        # Try alternative path
        input_file = "../raw_corpus.txt"
        if not os.path.exists(input_file):
            print("ERROR: raw_corpus.txt not found!")
            print("Please place raw_corpus.txt in the project root directory")
            sys.exit(1)

    # Run preprocessing
    sentences, stats = preprocess_corpus(input_file, output_dir)

    print(f"Next step: Run split_corpus.py to create train/val/test splits")
