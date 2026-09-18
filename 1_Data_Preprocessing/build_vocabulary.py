"""
Phase 2.2: Build a frequency-ordered Bangla vocabulary from the clean corpus.
"""

from collections import Counter
import csv
from pathlib import Path
import unicodedata


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data/processed/clean_corpus.txt"
RESOURCES_FOLDER = PROJECT_ROOT / "resources"
DICTIONARY_FILE = RESOURCES_FOLDER / "bangla_dictionary.txt"
FREQUENCY_FILE = RESOURCES_FOLDER / "vocabulary_frequency.csv"


def is_bangla_letter_or_mark(character):
    """Return whether a character is a Bangla letter or combining mark."""

    return (
        "\u0980" <= character <= "\u09FF"
        and unicodedata.category(character)[0] in {"L", "M"}
    )


def is_bangla_digit(character):
    """Return whether a character is a Bangla digit."""

    return "০" <= character <= "৯"


def tokenize_bangla_words(sentence):
    """Extract Bangla words while discarding punctuation and standalone numbers."""

    tokens = []
    current_token = []

    def add_current_token():
        if not current_token:
            return

        token = "".join(current_token)
        if any(is_bangla_letter_or_mark(character) for character in token):
            tokens.append(token)

        current_token.clear()

    for character in sentence:
        if is_bangla_letter_or_mark(character) or is_bangla_digit(character):
            current_token.append(character)
        else:
            add_current_token()

    add_current_token()
    return tokens


def build_vocabulary(sentences):
    """Count every Bangla token and return frequency-ranked vocabulary entries."""

    word_counts = Counter()
    total_tokens = 0

    for sentence in sentences:
        tokens = tokenize_bangla_words(sentence)
        word_counts.update(tokens)
        total_tokens += len(tokens)

    vocabulary = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
    return vocabulary, total_tokens


def save_dictionary(vocabulary, output_file):
    """Save one frequency-ordered Bangla word per line."""

    content = "\n".join(word for word, _ in vocabulary)
    if content:
        content += "\n"

    output_file.write_text(content, encoding="utf-8")


def save_frequency_csv(vocabulary, output_file):
    """Save frequency-ordered vocabulary entries to a UTF-8 CSV file."""

    with output_file.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["word", "frequency"])
        writer.writerows(vocabulary)


def print_summary(vocabulary, total_tokens):
    """Print vocabulary statistics and the 20 most frequent words."""

    print("\n" + "=" * 56)
    print("BANGLA VOCABULARY SUMMARY")
    print("=" * 56)
    print(f"Total tokens processed: {total_tokens:,}")
    print(f"Unique vocabulary size: {len(vocabulary):,}")
    print("\nTop 20 most frequent Bangla words:")

    for rank, (word, frequency) in enumerate(vocabulary[:20], start=1):
        print(f"{rank:>2}. {word} ({frequency:,})")

    print(f"\nDictionary file: {DICTIONARY_FILE}")
    print(f"Frequency CSV file: {FREQUENCY_FILE}")


def main():
    """Read the clean corpus, build vocabulary files, and print a summary."""

    if not INPUT_FILE.is_file():
        print(f"Clean corpus not found: {INPUT_FILE}")
        return

    sentences = INPUT_FILE.read_text(encoding="utf-8").splitlines()
    vocabulary, total_tokens = build_vocabulary(sentences)

    RESOURCES_FOLDER.mkdir(parents=True, exist_ok=True)
    save_dictionary(vocabulary, DICTIONARY_FILE)
    save_frequency_csv(vocabulary, FREQUENCY_FILE)
    print_summary(vocabulary, total_tokens)


if __name__ == "__main__":
    main()
