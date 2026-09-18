"""
Phase 2.1: Preprocess the collected Bangla sentence corpus.
"""

from pathlib import Path
import re
import unicodedata


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data/raw/raw_corpus.txt"
OUTPUT_FILE = PROJECT_ROOT / "data/processed/clean_corpus.txt"

MIN_SENTENCE_LENGTH = 20
MAX_SENTENCE_LENGTH = 250

INVISIBLE_CHARACTER_PATTERN = re.compile(
    r"[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060-\u2064\ufeff]"
)
URL_PATTERN = re.compile(r"(?:https?://|www\.)", re.IGNORECASE)
LATIN_LETTER_PATTERN = re.compile(r"[A-Za-z]")
BANGLA_CHARACTER_PATTERN = re.compile(r"[\u0980-\u09FF]")


def normalize_unicode(text):
    """Convert text to Unicode NFC form."""

    return unicodedata.normalize("NFC", text)


def remove_invisible_characters(text):
    """Remove zero-width, byte-order, and invisible Unicode marks."""

    return INVISIBLE_CHARACTER_PATTERN.sub("", text)


def normalize_bangla_punctuation_spacing(text):
    """Remove spaces before punctuation and add one after sentence terminators."""

    text = re.sub(r"\s+([।,;:?!])", r"\1", text)
    return re.sub(r"([।?!])(?=[^\s।?!])", r"\1 ", text)


def normalize_whitespace(text):
    """Collapse repeated whitespace and trim the result."""

    return re.sub(r"\s+", " ", text).strip()


def preprocess_sentence(sentence):
    """Apply the required normalization steps to one sentence in order."""

    sentence = normalize_unicode(sentence)
    sentence = remove_invisible_characters(sentence)
    sentence = normalize_bangla_punctuation_spacing(sentence)
    return normalize_whitespace(sentence)


def has_bangla_characters(sentence):
    """Return whether a sentence contains at least one Bangla Unicode character."""

    return bool(BANGLA_CHARACTER_PATTERN.search(sentence))


def is_valid_length(sentence):
    """Return whether sentence length is inside the allowed character range."""

    return MIN_SENTENCE_LENGTH <= len(sentence) <= MAX_SENTENCE_LENGTH


def clean_corpus(raw_sentences):
    """Normalize, deduplicate, filter, and preserve the first-occurrence order."""

    clean_sentences = []
    seen_sentences = set()
    statistics = {
        "duplicates_removed": 0,
        "latin_letter_sentences_removed": 0,
        "url_sentences_removed": 0,
        "empty_invalid_sentences_removed": 0,
    }

    for raw_sentence in raw_sentences:
        sentence = preprocess_sentence(raw_sentence)

        if sentence in seen_sentences:
            statistics["duplicates_removed"] += 1
            continue

        seen_sentences.add(sentence)

        if not sentence:
            statistics["empty_invalid_sentences_removed"] += 1
            continue

        if URL_PATTERN.search(sentence):
            statistics["url_sentences_removed"] += 1
            continue

        if LATIN_LETTER_PATTERN.search(sentence):
            statistics["latin_letter_sentences_removed"] += 1
            continue

        if not is_valid_length(sentence) or not has_bangla_characters(sentence):
            statistics["empty_invalid_sentences_removed"] += 1
            continue

        clean_sentences.append(sentence)

    return clean_sentences, statistics


def read_raw_corpus(input_file):
    """Read the raw corpus as its original one-sentence-per-line entries."""

    return input_file.read_text(encoding="utf-8").splitlines()


def save_clean_corpus(sentences, output_file):
    """Write the cleaned corpus as one UTF-8 sentence per line."""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(sentences)
    if content:
        content += "\n"

    output_file.write_text(content, encoding="utf-8")


def print_summary(input_count, output_count, statistics, output_file):
    """Print the required preprocessing summary."""

    print("\n" + "=" * 56)
    print("BANGLA CORPUS PREPROCESSING SUMMARY")
    print("=" * 56)
    print(f"Input sentence count: {input_count:,}")
    print(f"Output sentence count: {output_count:,}")
    print(f"Duplicates removed: {statistics['duplicates_removed']:,}")
    print(
        "Latin-letter sentences removed: "
        f"{statistics['latin_letter_sentences_removed']:,}"
    )
    print(f"URL sentences removed: {statistics['url_sentences_removed']:,}")
    print(
        "Empty/invalid sentences removed: "
        f"{statistics['empty_invalid_sentences_removed']:,}"
    )
    print(f"Output file path: {output_file}")


def main():
    """Run Phase 2.1 preprocessing from the raw corpus to the clean corpus."""

    if not INPUT_FILE.is_file():
        print(f"Raw corpus not found: {INPUT_FILE}")
        return

    raw_sentences = read_raw_corpus(INPUT_FILE)
    clean_sentences, statistics = clean_corpus(raw_sentences)
    save_clean_corpus(clean_sentences, OUTPUT_FILE)
    print_summary(
        input_count=len(raw_sentences),
        output_count=len(clean_sentences),
        statistics=statistics,
        output_file=OUTPUT_FILE,
    )


if __name__ == "__main__":
    main()
