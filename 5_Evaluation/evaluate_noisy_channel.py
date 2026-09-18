"""Evaluate the Bangla noisy-channel spelling correction model."""

from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import zip_longest
from pathlib import Path

import pandas as pd
from tqdm import tqdm


MODULE_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIRECTORY.parent
TEST_FILE = PROJECT_ROOT / "data" / "noisy" / "test_parallel.csv"
OUTPUT_DIRECTORY = PROJECT_ROOT / "outputs" / "noisy_channel"
EXPECTED_ERROR_TYPES = ("phonetic", "visual", "keyboard", "split", "run_on", "none")

if str(PROJECT_ROOT / "3_Noisy_Channel_Model") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "3_Noisy_Channel_Model"))

from inference_nc import correct_sentence


def _tokens(sentence: str) -> list[str]:
    """Split a sentence into the whitespace-separated tokens used for metrics."""
    return sentence.split()


def _calculate_word_metrics(results: list[dict[str, object]]) -> tuple[int, int, int, int]:
    """Return total words, correct words, noisy words, and corrected words."""
    total_words = correct_words = noisy_words = corrected_words = 0
    for result in results:
        clean_tokens = _tokens(str(result["clean_sentence"]))
        noisy_tokens = _tokens(str(result["noisy_sentence"]))
        predicted_tokens = _tokens(str(result["predicted_sentence"]))
        total_words += len(clean_tokens)

        for clean_token, predicted_token in zip_longest(
            clean_tokens,
            predicted_tokens,
            fillvalue=None,
        ):
            if clean_token is not None and predicted_token == clean_token:
                correct_words += 1

        for clean_token, noisy_token, predicted_token in zip_longest(
            clean_tokens,
            noisy_tokens,
            predicted_tokens,
            fillvalue=None,
        ):
            if noisy_token != clean_token:
                noisy_words += 1
                if predicted_token == clean_token:
                    corrected_words += 1

    return total_words, correct_words, noisy_words, corrected_words


def _accuracy(correct: int, total: int) -> float:
    """Return an accuracy value, using zero for an empty group."""
    return correct / total if total else 0.0


def _predict_row(row: tuple[str, str, str]) -> dict[str, object]:
    """Predict one row using the existing inference engine."""
    clean_sentence, noisy_sentence, error_type = row
    predicted_sentence = correct_sentence(noisy_sentence)
    return {
        "noisy_sentence": noisy_sentence,
        "predicted_sentence": predicted_sentence,
        "clean_sentence": clean_sentence,
        "error_type": error_type,
        "sentence_correct": predicted_sentence == clean_sentence,
    }


def evaluate() -> tuple[pd.DataFrame, dict[str, object], pd.DataFrame]:
    """Run inference over the held-out test set and calculate all metrics."""
    input_data = pd.read_csv(TEST_FILE, encoding="utf-8")
    required_columns = {"clean_sentence", "noisy_sentence", "error_type"}
    missing_columns = required_columns.difference(input_data.columns)
    if missing_columns:
        raise ValueError(f"Missing input columns: {sorted(missing_columns)}")

    rows = [
        (str(row.clean_sentence), str(row.noisy_sentence), str(row.error_type))
        for row in input_data.itertuples(index=False)
    ]
    worker_count = min(os.cpu_count() or 1, 8)
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        results = list(
            tqdm(
                executor.map(_predict_row, rows, chunksize=8),
                total=len(rows),
                desc="Evaluating noisy-channel model",
            )
        )

    predictions = pd.DataFrame(results)
    row_count_passed = len(predictions) == len(input_data)
    missing_predictions = predictions["predicted_sentence"].isna().any()
    predictions_passed = not missing_predictions
    print(f"Row count verification: {'PASS' if row_count_passed else 'FAIL'}")
    print(f"Missing prediction verification: {'PASS' if predictions_passed else 'FAIL'}")
    if not row_count_passed or not predictions_passed:
        raise ValueError("Evaluation self-check failed; outputs were not saved.")

    total_words, correct_words, noisy_words, corrected_words = _calculate_word_metrics(results)
    sentence_correct_count = int(predictions["sentence_correct"].sum())
    metrics = {
        "total_sentences": len(results),
        "sentence_accuracy": _accuracy(sentence_correct_count, len(results)),
        "total_words": total_words,
        "word_accuracy": _accuracy(correct_words, total_words),
        "noisy_words": noisy_words,
        "corrected_words": corrected_words,
        "correction_accuracy": _accuracy(corrected_words, noisy_words),
    }

    error_type_rows: list[dict[str, object]] = []
    for error_type in EXPECTED_ERROR_TYPES:
        type_predictions = predictions[predictions["error_type"] == error_type]
        total = len(type_predictions)
        correct = int(type_predictions["sentence_correct"].sum())
        error_type_rows.append(
            {
                "error_type": error_type,
                "total": total,
                "correct": correct,
                "accuracy": _accuracy(correct, total),
            }
        )

    return predictions, metrics, pd.DataFrame(error_type_rows)


def save_outputs(
    predictions: pd.DataFrame,
    metrics: dict[str, object],
    error_type_accuracy: pd.DataFrame,
) -> None:
    """Save evaluation predictions and metrics as UTF-8 files."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(
        OUTPUT_DIRECTORY / "predictions.csv",
        index=False,
        encoding="utf-8",
    )
    with (OUTPUT_DIRECTORY / "metrics.json").open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, ensure_ascii=False, indent=2)
    error_type_accuracy.to_csv(
        OUTPUT_DIRECTORY / "error_type_accuracy.csv",
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    predictions, metrics, error_type_accuracy = evaluate()
    save_outputs(predictions, metrics, error_type_accuracy)

    print("# ========================================================")
    print("BANGLA NOISY CHANNEL EVALUATION")
    print(f"Test sentences: {metrics['total_sentences']}")
    print(f"Sentence accuracy: {metrics['sentence_accuracy']:.4f}")
    print(f"Word accuracy: {metrics['word_accuracy']:.4f}")
    print(f"Correction accuracy: {metrics['correction_accuracy']:.4f}")
    print("\nError-type accuracy table:")
    print(error_type_accuracy.to_string(index=False))
    print(f"\nOutput folder: {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()
