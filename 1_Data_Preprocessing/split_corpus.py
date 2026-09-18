"""
Phase 2.3: Split the clean Bangla corpus into train, validation, and test sets.
"""

from pathlib import Path
import random


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data/processed/clean_corpus.txt"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data/splits"
TRAIN_FILE = OUTPUT_DIRECTORY / "train_set.txt"
VALIDATION_FILE = OUTPUT_DIRECTORY / "validation_set.txt"
TEST_FILE = OUTPUT_DIRECTORY / "test_set.txt"

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.10
RANDOM_SEED = 42


def read_sentences(input_file):
    """Read the corpus as one sentence per line without altering sentence text."""

    return input_file.read_text(encoding="utf-8").splitlines()


def split_sentences(sentences):
    """Shuffle once with seed 42 and return 70/10/20 corpus splits."""

    shuffled_sentences = list(sentences)
    random.seed(RANDOM_SEED)
    random.shuffle(shuffled_sentences)

    total_sentences = len(shuffled_sentences)
    train_count = int(total_sentences * TRAIN_RATIO)
    validation_count = int(total_sentences * VALIDATION_RATIO)

    train_sentences = shuffled_sentences[:train_count]
    validation_sentences = shuffled_sentences[
        train_count:train_count + validation_count
    ]
    test_sentences = shuffled_sentences[train_count + validation_count:]

    return train_sentences, validation_sentences, test_sentences


def verify_splits(input_count, train_sentences, validation_sentences, test_sentences):
    """Check split counts and sentence overlap between every pair of splits."""

    train_set = set(train_sentences)
    validation_set = set(validation_sentences)
    test_set = set(test_sentences)

    overlaps = {
        "train_validation": bool(train_set & validation_set),
        "train_test": bool(train_set & test_set),
        "validation_test": bool(validation_set & test_set),
    }

    return {
        "total_matches_input": (
            len(train_sentences) + len(validation_sentences) + len(test_sentences)
            == input_count
        ),
        "overlap_exists": any(overlaps.values()),
        "pairwise_overlaps": overlaps,
    }


def save_split(sentences, output_file):
    """Save one UTF-8 sentence per line without changing sentence content."""

    content = "\n".join(sentences)
    if content:
        content += "\n"

    output_file.write_text(content, encoding="utf-8")


def print_summary(input_count, train_sentences, validation_sentences, test_sentences, verification):
    """Print split counts and verification results."""

    total_after_split = (
        len(train_sentences) + len(validation_sentences) + len(test_sentences)
    )

    print("\n" + "=" * 56)
    print("CORPUS SPLIT SUMMARY")
    print("=" * 56)
    print(f"Input sentence count: {input_count:,}")
    print(f"Train count: {len(train_sentences):,}")
    print(f"Validation count: {len(validation_sentences):,}")
    print(f"Test count: {len(test_sentences):,}")
    print(f"Total after split: {total_after_split:,}")
    print(
        "Total matches input: "
        f"{'PASS' if verification['total_matches_input'] else 'FAIL'}"
    )
    print(
        "Overlap check result: "
        f"{'NO OVERLAP' if not verification['overlap_exists'] else 'OVERLAP FOUND'}"
    )
    print(f"Output directory path: {OUTPUT_DIRECTORY}")


def main():
    """Read, split, verify, save, and report the clean corpus splits."""

    if not INPUT_FILE.is_file():
        print(f"Clean corpus not found: {INPUT_FILE}")
        return

    sentences = read_sentences(INPUT_FILE)
    train_sentences, validation_sentences, test_sentences = split_sentences(sentences)
    verification = verify_splits(
        len(sentences),
        train_sentences,
        validation_sentences,
        test_sentences,
    )

    if not verification["total_matches_input"] or verification["overlap_exists"]:
        print_summary(
            len(sentences),
            train_sentences,
            validation_sentences,
            test_sentences,
            verification,
        )
        raise RuntimeError("Split verification failed; output files were not written.")

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    save_split(train_sentences, TRAIN_FILE)
    save_split(validation_sentences, VALIDATION_FILE)
    save_split(test_sentences, TEST_FILE)
    print_summary(
        len(sentences),
        train_sentences,
        validation_sentences,
        test_sentences,
        verification,
    )


if __name__ == "__main__":
    main()
