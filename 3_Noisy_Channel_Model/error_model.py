"""Build character-substitution statistics for the Bangla noisy-channel model."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_PARALLEL_PATH = PROJECT_ROOT / "data" / "noisy" / "train_parallel.csv"
MODELS_DIRECTORY = PROJECT_ROOT / "models"


def extract_substitutions(clean_sentence: str, noisy_sentence: str) -> list[tuple[str, str]]:
    """Align two sentences and return only their differing character pairs.

    Equal-length rows can be compared directly.  For structural edits, sequence
    alignment keeps later text aligned; insertions/deletions remain uncounted.
    """
    if len(clean_sentence) == len(noisy_sentence):
        return [
            (source, observed)
            for source, observed in zip(clean_sentence, noisy_sentence)
            if source != observed
        ]

    substitutions: list[tuple[str, str]] = []
    matcher = SequenceMatcher(None, clean_sentence, noisy_sentence, autojunk=False)
    for operation, clean_start, clean_end, noisy_start, noisy_end in matcher.get_opcodes():
        if operation == "replace":
            substitutions.extend(
                (source, observed)
                for source, observed in zip(
                    clean_sentence[clean_start:clean_end],
                    noisy_sentence[noisy_start:noisy_end],
                )
                if source != observed
            )
    return substitutions


def build_error_statistics(input_path: Path) -> tuple[dict, Counter, int]:
    """Read parallel CSV rows and collect substitution and error-type counts."""
    confusion_counts: defaultdict[str, Counter] = defaultdict(Counter)
    error_type_counts: Counter = Counter()
    pair_count = 0

    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)
        for row in tqdm(reader, desc="Processing training pairs", unit="pair"):
            clean_sentence = row["clean_sentence"]
            noisy_sentence = row["noisy_sentence"]
            error_type_counts[row["error_type"]] += 1
            pair_count += 1

            for source, observed in extract_substitutions(clean_sentence, noisy_sentence):
                confusion_counts[source][observed] += 1

    return {
        source: dict(observed_counts)
        for source, observed_counts in confusion_counts.items()
    }, error_type_counts, pair_count


def normalize_confusion_counts(confusion_counts: dict) -> dict:
    """Convert raw observed counts into P(observed | source) distributions."""
    probabilities = {}
    for source, observed_counts in confusion_counts.items():
        total = sum(observed_counts.values())
        probabilities[source] = {
            observed: count / total
            for observed, count in observed_counts.items()
        }
    return probabilities


def save_json(output_path: Path, data: dict) -> None:
    """Write human-readable UTF-8 JSON output."""
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=2)


def print_summary(confusion_counts: dict, error_type_counts: Counter, pair_count: int) -> None:
    """Print the requested corpus, error-type, and substitution overview."""
    total_substitutions = sum(
        count for observed_counts in confusion_counts.values() for count in observed_counts.values()
    )
    unique_substitutions = sum(len(observed_counts) for observed_counts in confusion_counts.values())
    substitution_counts = Counter({
        f"{source} → {observed}": count
        for source, observed_counts in confusion_counts.items()
        for observed, count in observed_counts.items()
    })

    print("=" * 56)
    print("BANGLA ERROR MODEL SUMMARY")
    print("=" * 56)
    print(f"Training sentence pairs: {pair_count}")
    print(f"Total substitutions observed: {total_substitutions}")
    print(f"Unique source characters: {len(confusion_counts)}")
    print(f"Unique observed substitutions: {unique_substitutions}")

    print("\nError type distribution:")
    for error_type in ("phonetic", "visual", "keyboard", "split", "run_on", "none"):
        print(f"{error_type}: {error_type_counts[error_type]}")

    print("\nTop 20 character substitutions:")
    for substitution, count in substitution_counts.most_common(20):
        print(f"{substitution}: {count}")

    print(f"\nOutput folder: {MODELS_DIRECTORY}")


def main() -> None:
    """Build, save, and report substitution statistics from training pairs."""
    confusion_counts, error_type_counts, pair_count = build_error_statistics(
        TRAIN_PARALLEL_PATH
    )
    confusion_probabilities = normalize_confusion_counts(confusion_counts)

    MODELS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    save_json(MODELS_DIRECTORY / "confusion_counts.json", confusion_counts)
    save_json(MODELS_DIRECTORY / "confusion_probabilities.json", confusion_probabilities)
    save_json(MODELS_DIRECTORY / "error_type_distribution.json", dict(error_type_counts))
    print_summary(confusion_counts, error_type_counts, pair_count)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
