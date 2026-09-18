"""Create reproducible noisy Bangla datasets from the clean sentence splits."""

from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path

from error_patterns import apply_error


# Seed once for repeatable replacement-position selection across all splits.
random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPLITS_DIRECTORY = PROJECT_ROOT / "data" / "splits"
NOISY_DIRECTORY = PROJECT_ROOT / "data" / "noisy"

# Every clean sentence is emitted once for each type, in this exact order.
ERROR_TYPES = ("phonetic", "visual", "keyboard", "split", "run_on")
SUMMARY_ORDER = (*ERROR_TYPES, "none")
SPLITS = ("train", "validation", "test")
MAX_ATTEMPTS = 3


def read_sentences(input_path: Path) -> list[str]:
    """Read UTF-8 sentences while retaining their order and empty lines."""
    with input_path.open("r", encoding="utf-8") as input_file:
        return [line.rstrip("\r\n") for line in input_file]


def generate_noisy_sentence(clean_sentence: str, error_type: str) -> tuple[str, str]:
    """Apply one specified error type, retrying it up to three times if needed."""
    for _ in range(MAX_ATTEMPTS):
        noisy_sentence = apply_error(clean_sentence, error_type)
        if noisy_sentence != clean_sentence:
            return noisy_sentence, error_type
    return clean_sentence, "none"


def generate_parallel_rows(sentences: list[str]) -> tuple[list[tuple[str, str, str]], Counter]:
    """Create five ordered clean/noisy rows for every input sentence."""
    rows: list[tuple[str, str, str]] = []
    counts: Counter = Counter()
    for clean_sentence in sentences:
        for requested_type in ERROR_TYPES:
            noisy_sentence, applied_type = generate_noisy_sentence(
                clean_sentence,
                requested_type,
            )
            rows.append((clean_sentence, noisy_sentence, applied_type))
            counts[applied_type] += 1
    return rows, counts


def write_noisy_text(output_path: Path, rows: list[tuple[str, str, str]]) -> None:
    """Write the noisy side of parallel rows as a UTF-8 line-aligned text file."""
    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        for _, noisy_sentence, _ in rows:
            output_file.write(f"{noisy_sentence}\n")


def write_parallel_csv(output_path: Path, rows: list[tuple[str, str, str]]) -> None:
    """Write clean/noisy sentence pairs and their applied error type as UTF-8 CSV."""
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(("clean_sentence", "noisy_sentence", "error_type"))
        writer.writerows(rows)


def print_summary(split_name: str, clean_total: int, counts: Counter) -> None:
    """Print generation totals in a consistent, human-readable format."""
    print(f"{split_name.upper()} SUMMARY")
    print()
    print(f"Clean sentences: {clean_total}")
    print(f"Generated noisy sentences: {clean_total * len(ERROR_TYPES)}")
    print()
    for error_type in SUMMARY_ORDER:
        label = "Run-on" if error_type == "run_on" else error_type.capitalize()
        print(f"{label}: {counts[error_type]}")


def generate_split(split_name: str) -> tuple[int, int]:
    """Generate the two noisy outputs for one named clean split."""
    clean_path = SPLITS_DIRECTORY / f"{split_name}_set.txt"
    sentences = read_sentences(clean_path)
    rows, counts = generate_parallel_rows(sentences)

    write_noisy_text(NOISY_DIRECTORY / f"{split_name}_noisy.txt", rows)
    write_parallel_csv(NOISY_DIRECTORY / f"{split_name}_parallel.csv", rows)
    print_summary(split_name, len(sentences), counts)
    return len(sentences), len(rows)


def main() -> None:
    """Generate line-aligned noisy text and parallel CSV files for all splits."""
    NOISY_DIRECTORY.mkdir(parents=True, exist_ok=True)
    total_clean_sentences = 0
    total_noisy_sentences = 0
    for split_name in SPLITS:
        clean_count, noisy_count = generate_split(split_name)
        total_clean_sentences += clean_count
        total_noisy_sentences += noisy_count

    print("TOTAL CLEAN SENTENCES")
    print(total_clean_sentences)
    print("TOTAL NOISY SENTENCES")
    print(total_noisy_sentences)
    print("TOTAL PARALLEL PAIRS")
    print(total_noisy_sentences)


if __name__ == "__main__":
    main()
