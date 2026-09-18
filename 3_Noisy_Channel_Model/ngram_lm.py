"""Build and save unigram and bigram counts for the noisy-channel model."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_PATH = PROJECT_ROOT / "data" / "splits" / "train_set.txt"
MODELS_DIRECTORY = PROJECT_ROOT / "models"
_BANGLA_BLOCK_PATTERN = re.compile(r"[\u0980-\u09FF]+")


def tokenize_bangla_words(sentence: str) -> list[str]:
    """Return Bangla word tokens, excluding Bangla digits and punctuation."""
    return [
        token
        for token in _BANGLA_BLOCK_PATTERN.findall(sentence)
        if all(unicodedata.category(character)[0] in {"L", "M"} for character in token)
    ]


def read_sentences(input_path: Path) -> list[str]:
    """Read the UTF-8 training split, retaining one sentence per input line."""
    with input_path.open("r", encoding="utf-8") as input_file:
        return [line.rstrip("\r\n") for line in input_file]


def build_ngram_counts(sentences: list[str]) -> tuple[Counter, Counter, int]:
    """Count unigrams and consecutive bigrams from Bangla-tokenized sentences."""
    unigram_counts: Counter = Counter()
    bigram_counts: Counter = Counter()
    total_tokens = 0

    for sentence in tqdm(sentences, desc="Processing training sentences", unit="sentence"):
        tokens = tokenize_bangla_words(sentence)
        unigram_counts.update(tokens)
        bigram_counts.update(f"{first}||{second}" for first, second in zip(tokens, tokens[1:]))
        total_tokens += len(tokens)

    return unigram_counts, bigram_counts, total_tokens


def save_json(output_path: Path, data: dict) -> None:
    """Save JSON with readable UTF-8 Bangla text."""
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=2)


def print_summary(stats: dict, unigrams: Counter, bigrams: Counter) -> None:
    """Print corpus totals and the 15 most frequent unigram/bigram counts."""
    print("LANGUAGE MODEL SUMMARY")
    print(f"Total sentences: {stats['total_sentences']}")
    print(f"Total tokens: {stats['total_tokens']}")
    print(f"Unique unigrams: {stats['unique_unigrams']}")
    print(f"Unique bigrams: {stats['unique_bigrams']}")

    print("\nTop 15 unigram words:")
    for word, count in unigrams.most_common(15):
        print(f"{word}: {count}")

    print("\nTop 15 bigram pairs:")
    for pair, count in bigrams.most_common(15):
        print(f"{pair}: {count}")


def main() -> None:
    """Build counts from the training split and save the model artifacts."""
    sentences = read_sentences(TRAIN_PATH)
    unigram_counts, bigram_counts, total_tokens = build_ngram_counts(sentences)
    stats = {
        "total_sentences": len(sentences),
        "total_tokens": total_tokens,
        "unique_unigrams": len(unigram_counts),
        "unique_bigrams": len(bigram_counts),
    }

    MODELS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    save_json(MODELS_DIRECTORY / "unigram_counts.json", dict(unigram_counts))
    save_json(MODELS_DIRECTORY / "bigram_counts.json", dict(bigram_counts))
    save_json(MODELS_DIRECTORY / "lm_stats.json", stats)
    print_summary(stats, unigram_counts, bigram_counts)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
