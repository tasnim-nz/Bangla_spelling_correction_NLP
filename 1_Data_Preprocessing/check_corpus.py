"""
Inspect the collected Bangla corpus without modifying it.
"""

from pathlib import Path
import argparse
import random
import re


CORPUS_FILES = {
    "raw": Path("data/raw/raw_corpus.txt"),
    "processed": Path("data/processed/clean_corpus.txt"),
}
LATIN_LETTER_PATTERN = re.compile(r"[A-Za-z]")
URL_PATTERN = re.compile(r"(?:https?://|www\.)", re.IGNORECASE)
BANGLA_CHARACTER_PATTERN = re.compile(r"[\u0980-\u09FF]")
BANGLA_DIGIT_PATTERN = re.compile(r"[0-9০-৯]")


def parse_arguments():
    """Read the optional corpus type from the command line."""

    parser = argparse.ArgumentParser(description="Print a Bangla corpus quality report.")
    parser.add_argument(
        "corpus_type",
        nargs="?",
        choices=CORPUS_FILES,
        default="raw",
        help="Corpus to analyze: raw (default) or processed.",
    )
    return parser.parse_args()


def find_corpus_file(corpus_type):
    """Return the corpus path for common project launch locations."""

    script_directory = Path(__file__).resolve().parent
    corpus_path = CORPUS_FILES[corpus_type]
    candidate_paths = [
        corpus_path,
        script_directory.parent / corpus_path,
    ]

    for path in candidate_paths:
        if path.is_file():
            return path

    checked_paths = "\n".join(f"  - {path.resolve()}" for path in candidate_paths)
    raise FileNotFoundError(f"Corpus file was not found. Checked:\n{checked_paths}")


def read_sentences(corpus_path):
    """Read non-empty corpus lines without changing their text."""

    lines = corpus_path.read_text(encoding="utf-8").splitlines()
    return [line for line in lines if line.strip()]


def is_mostly_digits(sentence):
    """Return True when more than half of a sentence's visible characters are digits."""

    visible_characters = [character for character in sentence if not character.isspace()]
    if not visible_characters:
        return False

    digit_count = sum(
        bool(BANGLA_DIGIT_PATTERN.fullmatch(character))
        for character in visible_characters
    )
    return digit_count / len(visible_characters) > 0.50


def calculate_metrics(sentences):
    """Calculate corpus-quality statistics from the original sentence lines."""

    unique_sentences = set(sentences)
    lengths = [len(sentence) for sentence in sentences]
    visible_characters = [
        character
        for sentence in sentences
        for character in sentence
        if not character.isspace()
    ]
    bangla_character_count = sum(
        bool(BANGLA_CHARACTER_PATTERN.fullmatch(character))
        for character in visible_characters
    )

    return {
        "total_sentences": len(sentences),
        "unique_sentences": len(unique_sentences),
        "duplicate_sentences": len(sentences) - len(unique_sentences),
        "average_length": sum(lengths) / len(lengths) if lengths else 0,
        "minimum_length": min(lengths) if lengths else 0,
        "maximum_length": max(lengths) if lengths else 0,
        "latin_letter_sentences": sum(
            bool(LATIN_LETTER_PATTERN.search(sentence)) for sentence in sentences
        ),
        "url_sentences": sum(bool(URL_PATTERN.search(sentence)) for sentence in sentences),
        "mostly_digit_sentences": sum(is_mostly_digits(sentence) for sentence in sentences),
        "bangla_character_percentage": (
            bangla_character_count / len(visible_characters) * 100
            if visible_characters
            else 0
        ),
    }


def print_sentence_group(title, sentences):
    """Print a titled group of sentences."""

    print(f"\n{title}")
    print("-" * len(title))

    for number, sentence in enumerate(sentences, start=1):
        print(f"{number:>2}. {sentence}")


def main():
    """Load the corpus and print its quality report."""

    arguments = parse_arguments()

    try:
        corpus_path = find_corpus_file(arguments.corpus_type)
    except FileNotFoundError as error:
        print(error)
        return

    sentences = read_sentences(corpus_path)
    metrics = calculate_metrics(sentences)
    sample_size = min(10, len(sentences))

    print("=" * 60)
    print("BANGLA CORPUS QUALITY REPORT")
    print("=" * 60)
    print(f"Corpus file: {corpus_path.resolve()}")
    print(f"Total sentences: {metrics['total_sentences']:,}")
    print(f"Unique sentences: {metrics['unique_sentences']:,}")
    print(f"Duplicate sentences: {metrics['duplicate_sentences']:,}")
    print(f"Average sentence length: {metrics['average_length']:.2f} characters")
    print(f"Minimum sentence length: {metrics['minimum_length']} characters")
    print(f"Maximum sentence length: {metrics['maximum_length']} characters")
    print(f"Sentences with Latin letters: {metrics['latin_letter_sentences']:,}")
    print(f"Sentences with URLs: {metrics['url_sentences']:,}")
    print(f"Mostly-digit sentences: {metrics['mostly_digit_sentences']:,}")
    print(
        "Bangla Unicode characters: "
        f"{metrics['bangla_character_percentage']:.2f}% "
        "of non-whitespace characters"
    )

    print_sentence_group("First 10 sentences", sentences[:10])
    print_sentence_group("10 random sentences", random.sample(sentences, sample_size))
    print_sentence_group(
        "10 longest sentences",
        sorted(sentences, key=len, reverse=True)[:10],
    )
    print_sentence_group(
        "10 shortest valid sentences",
        sorted(sentences, key=len)[:10],
    )


if __name__ == "__main__":
    main()
