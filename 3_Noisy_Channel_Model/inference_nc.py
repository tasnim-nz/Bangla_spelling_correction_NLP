"""Log-space inference for the Bangla noisy-channel spell corrector."""

from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from pathlib import Path


MODULE_DIRECTORY = Path(__file__).resolve().parent
if str(MODULE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(MODULE_DIRECTORY))

from candidate_generator import DICTIONARY, generate_candidates


PROJECT_ROOT = MODULE_DIRECTORY.parent
MODELS_DIRECTORY = PROJECT_ROOT / "models"
SMOOTHING_PROBABILITY = 1e-6
CONFIDENCE_THRESHOLD = 1.5


def _load_json(filename: str) -> dict:
    """Load one UTF-8 model JSON file from the project models directory."""
    with (MODELS_DIRECTORY / filename).open("r", encoding="utf-8") as model_file:
        return json.load(model_file)


# Load fixed model artifacts once when this module starts.
UNIGRAM_COUNTS = _load_json("unigram_counts.json")
BIGRAM_COUNTS = _load_json("bigram_counts.json")
LM_STATS = _load_json("lm_stats.json")
CONFUSION_PROBABILITIES = _load_json("confusion_probabilities.json")
TOTAL_TOKENS = LM_STATS["total_tokens"]
VOCABULARY_SIZE = LM_STATS["unique_unigrams"]


def unigram_probability(word: str) -> float:
    """Return the Laplace-smoothed unigram probability of a word."""
    return (UNIGRAM_COUNTS.get(word, 0) + 1) / (TOTAL_TOKENS + VOCABULARY_SIZE)


def bigram_probability(previous_word: str, current_word: str) -> float:
    """Return the Laplace-smoothed probability of a consecutive word pair."""
    bigram_key = f"{previous_word}||{current_word}"
    return (BIGRAM_COUNTS.get(bigram_key, 0) + 1) / (
        UNIGRAM_COUNTS.get(previous_word, 0) + VOCABULARY_SIZE
    )


def language_model_score(candidate: str, previous_word: str | None = None) -> float:
    """Return a candidate's unigram or context-conditioned bigram log score."""
    probability = (
        bigram_probability(previous_word, candidate)
        if previous_word
        else unigram_probability(candidate)
    )
    return math.log(probability)


def error_model_score(clean_word: str, noisy_word: str) -> float:
    """Return log P(noisy_word | clean_word) from observed substitutions.

    Only index-aligned substitutions are used in this phase.  Extra or missing
    characters are ignored, as insertion/deletion statistics are not modeled.
    """
    clean_start = noisy_start = 0
    while (
        clean_start < len(clean_word)
        and noisy_start < len(noisy_word)
        and clean_word[clean_start] == noisy_word[noisy_start]
    ):
        clean_start += 1
        noisy_start += 1

    clean_end, noisy_end = len(clean_word), len(noisy_word)
    while (
        clean_end > clean_start
        and noisy_end > noisy_start
        and clean_word[clean_end - 1] == noisy_word[noisy_end - 1]
    ):
        clean_end -= 1
        noisy_end -= 1

    clean_change = clean_word[clean_start:clean_end]
    noisy_change = noisy_word[noisy_start:noisy_end]
    # A different-sized middle span is an insertion/deletion (or a conjunct
    # expansion).  It has no model in this phase, so it contributes no penalty.
    if len(clean_change) != len(noisy_change):
        return 0.0

    probability = 1.0
    for clean_character, noisy_character in zip(clean_change, noisy_change):
        if clean_character != noisy_character:
            probability *= CONFUSION_PROBABILITIES.get(clean_character, {}).get(
                noisy_character,
                SMOOTHING_PROBABILITY,
            )
    return math.log(probability)


def noisy_channel_score(
    candidate: str,
    noisy_word: str,
    previous_word: str | None = None,
) -> float:
    """Combine language-model and error-model evidence in log space."""
    return language_model_score(candidate, previous_word) + error_model_score(
        candidate,
        noisy_word,
    )


def _orthographically_related(candidate: str, noisy_word: str) -> bool:
    """Return whether a candidate shares enough Bangla characters with a word."""
    noisy_characters = [character for character in noisy_word if _is_bangla_character(character)]
    candidate_characters = [character for character in candidate if _is_bangla_character(character)]
    overlap_row = [0] * (len(candidate_characters) + 1)
    for noisy_character in noisy_characters:
        previous_overlap = 0
        for index, candidate_character in enumerate(candidate_characters, start=1):
            saved_overlap = overlap_row[index]
            if noisy_character == candidate_character:
                overlap_row[index] = previous_overlap + 1
            else:
                overlap_row[index] = max(overlap_row[index], overlap_row[index - 1])
            previous_overlap = saved_overlap
    overlap = overlap_row[-1]
    return (
        abs(len(candidate) - len(noisy_word)) <= 1
        and overlap >= math.ceil(len(noisy_characters) / 2)
    )


def correct_word(noisy_word: str, previous_word: str | None = None) -> tuple[str, float]:
    """Return a correction only when an unknown word has strong evidence."""
    # Dictionary words are already valid Bangla spellings and should not be
    # changed merely because a more frequent word has a higher LM score.
    if noisy_word in DICTIONARY:
        return noisy_word, 0.0

    candidates = [
        candidate
        for candidate in generate_candidates(noisy_word)
        if _orthographically_related(candidate, noisy_word)
    ]
    if not candidates:
        return noisy_word, language_model_score(noisy_word, previous_word)

    candidate_scores = {
        candidate: noisy_channel_score(candidate, noisy_word, previous_word)
        for candidate in candidates
    }
    original_score = noisy_channel_score(noisy_word, noisy_word, previous_word)

    best_candidate = max(
        candidate_scores,
        key=lambda candidate: candidate_scores[candidate]
        - 0.5 * abs(len(candidate) - len(noisy_word)),
    )
    best_score = candidate_scores[best_candidate]
    if best_score - original_score < CONFIDENCE_THRESHOLD:
        return noisy_word, original_score
    return best_candidate, best_score


def _is_bangla_character(character: str) -> bool:
    """Return whether a character is a Bangla letter or combining mark."""
    return (
        "\u0980" <= character <= "\u09ff"
        and unicodedata.category(character)[0] in {"L", "M"}
    )


def _split_attached_punctuation(token: str) -> tuple[str, str, str]:
    """Separate leading/trailing punctuation while retaining the Bangla core."""
    start = 0
    while start < len(token) and not _is_bangla_character(token[start]):
        start += 1

    end = len(token)
    while end > start and not _is_bangla_character(token[end - 1]):
        end -= 1
    return token[:start], token[start:end], token[end:]


def correct_sentence(sentence: str) -> str:
    """Correct whitespace-separated Bangla words while preserving punctuation."""
    previous_word: str | None = None
    corrected_parts: list[str] = []

    for part in re.split(r"(\s+)", sentence):
        if not part or part.isspace():
            corrected_parts.append(part)
            continue

        prefix, noisy_word, suffix = _split_attached_punctuation(part)
        if noisy_word:
            corrected_word, _ = correct_word(noisy_word, previous_word)
            corrected_parts.append(prefix + corrected_word + suffix)
            previous_word = corrected_word
        else:
            corrected_parts.append(part)

    return "".join(corrected_parts)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for sample_sentence in (
        "বাংলাদেস একটি সুন্দর দেশ।",
        "তিণি আজ স্কুলে গেছেন।",
        "ভাংলাদেশ ক্রিকেট ভালোবাসে।",
        "লাইণে অনেক মানুষ দাঁড়িয়ে আছে।",
        "শিখখা জাতির মেরুদণ্ড।",
    ):
        print(f"Original: {sample_sentence}")
        print(f"Corrected: {correct_sentence(sample_sentence)}")
