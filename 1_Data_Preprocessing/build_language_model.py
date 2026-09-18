"""
Phase 1: Data Preprocessing - Step 3
Build n-gram Language Model

This script:
1. Loads training corpus
2. Tokenizes sentences
3. Builds unigram, bigram, trigram language models
4. Calculates probabilities
5. Saves language model for use in Noisy-Channel model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import defaultdict, Counter
import math
from utils.io_utils import read_lines, write_json, save_pickle
from utils.bangla_utils import tokenize_bangla_words


def build_ngram_model(sentences, n=2):
    """
    Build n-gram language model

    Args:
        sentences (list): List of sentences
        n (int): n for n-gram (1=unigram, 2=bigram, 3=trigram)

    Returns:
        dict: n-gram model with probabilities
    """
    model = defaultdict(Counter)

    # Generate n-grams and count
    for sentence in sentences:
        words = tokenize_bangla_words(sentence)

        # Add start and end tokens
        words = ['<START>'] + words + ['<END>']

        # Generate n-grams
        for i in range(len(words) - n + 1):
            history = tuple(words[i:i + n - 1])
            next_word = words[i + n - 1]
            model[history][next_word] += 1

    # Convert counts to probabilities (with Laplace smoothing)
    prob_model = {}
    vocab_size = sum(len(counter) for counter in model.values())

    for history, context in model.items():
        total_count = sum(context.values())
        prob_model[history] = {}

        for next_word, count in context.items():
            # Laplace smoothing: (count + 1) / (total + vocab_size)
            prob = (count + 1) / (total_count + vocab_size)
            prob_model[history][next_word] = prob

    return prob_model, vocab_size


def build_unigram_model(sentences):
    """
    Build unigram language model (word frequencies)

    Args:
        sentences (list): List of sentences

    Returns:
        dict: Unigram probabilities
    """
    word_counts = Counter()
    total_words = 0

    # Count all words
    for sentence in sentences:
        words = tokenize_bangla_words(sentence)
        word_counts.update(words)
        total_words += len(words)

    # Convert to probabilities
    unigram_model = {}
    vocab_size = len(word_counts)

    for word, count in word_counts.items():
        # Laplace smoothing
        prob = (count + 1) / (total_words + vocab_size)
        unigram_model[word] = prob

    return unigram_model, vocab_size


def build_language_models(train_corpus_file, output_dir):
    """
    Build all language models

    Args:
        train_corpus_file (str): Path to training corpus
        output_dir (str): Output directory
    """
    print("\n" + "="*70)
    print("PHASE 1: LANGUAGE MODEL TRAINING")
    print("="*70)

    # Step 1: Load training corpus
    print("\n[1/6] Loading training corpus...")
    sentences = read_lines(train_corpus_file)
    print(f"✓ Loaded {len(sentences)} sentences")

    # Step 2: Build unigram model
    print("\n[2/6] Building unigram model...")
    unigram_model, vocab_size = build_unigram_model(sentences)
    print(f"✓ Unigram model built")
    print(f"✓ Vocabulary size: {vocab_size:,}")

    # Step 3: Build bigram model
    print("\n[3/6] Building bigram model...")
    bigram_model, _ = build_ngram_model(sentences, n=2)
    print(f"✓ Bigram model built with {len(bigram_model)} contexts")

    # Step 4: Build trigram model
    print("\n[4/6] Building trigram model...")
    trigram_model, _ = build_ngram_model(sentences, n=3)
    print(f"✓ Trigram model built with {len(trigram_model)} contexts")

    # Step 5: Calculate model statistics
    print("\n[5/6] Calculating statistics...")

    total_words = sum(len(tokenize_bangla_words(s)) for s in sentences)
    avg_words = total_words / len(sentences)

    stats = {
        "total_sentences": len(sentences),
        "total_words": total_words,
        "vocabulary_size": vocab_size,
        "avg_words_per_sentence": round(avg_words, 2),
        "unigram_size": len(unigram_model),
        "bigram_contexts": len(bigram_model),
        "trigram_contexts": len(trigram_model)
    }

    print(f"✓ Total sentences: {stats['total_sentences']:,}")
    print(f"✓ Total words: {stats['total_words']:,}")
    print(f"✓ Vocabulary size: {stats['vocabulary_size']:,}")

    # Step 6: Save models
    print("\n[6/6] Saving models...")
    os.makedirs(output_dir, exist_ok=True)

    # Save unigram model
    unigram_file = os.path.join(output_dir, "unigram_model.pkl")
    save_pickle(unigram_file, unigram_model)
    print(f"✓ Saved unigram model: {unigram_file}")

    # Save bigram model
    bigram_file = os.path.join(output_dir, "bigram_model.pkl")
    save_pickle(bigram_file, bigram_model)
    print(f"✓ Saved bigram model: {bigram_file}")

    # Save trigram model
    trigram_file = os.path.join(output_dir, "trigram_model.pkl")
    save_pickle(trigram_file, trigram_model)
    print(f"✓ Saved trigram model: {trigram_file}")

    # Save statistics
    stats_file = os.path.join(output_dir, "lm_stats.json")
    write_json(stats_file, stats)
    print(f"✓ Saved statistics: {stats_file}")

    # Display top words from unigram model
    print("\n" + "-"*70)
    print("Top 20 Most Likely Words (Unigram Model)")
    print("-"*70)

    sorted_unigrams = sorted(unigram_model.items(), key=lambda x: x[1], reverse=True)
    for i, (word, prob) in enumerate(sorted_unigrams[:20], 1):
        print(f"{i:2}. {word:15} - P(w) = {prob:.6f}")

    print("\n" + "="*70)
    print("✓ LANGUAGE MODEL TRAINING COMPLETE")
    print("="*70)
    print(f"\nLanguage models saved:")
    print(f"  • Unigram: {len(unigram_model):,} unique words")
    print(f"  • Bigram: {len(bigram_model):,} bigram contexts")
    print(f"  • Trigram: {len(trigram_model):,} trigram contexts")
    print(f"\nReady for Noisy-Channel Model (Phase 3)\n")

    return unigram_model, bigram_model, trigram_model, stats


if __name__ == "__main__":
    # Paths
    train_corpus_file = "outputs/train_corpus.txt"
    output_dir = "outputs"

    # Check if train corpus exists
    if not os.path.exists(train_corpus_file):
        print("ERROR: train_corpus.txt not found!")
        print("Please run split_corpus.py first")
        sys.exit(1)

    # Build language models
    unigram, bigram, trigram, stats = build_language_models(
        train_corpus_file,
        output_dir
    )

    print("Language models are ready for use in Phase 3!")
