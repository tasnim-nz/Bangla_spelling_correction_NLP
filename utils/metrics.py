"""
Evaluation Metrics for Spelling Correction
"""

import numpy as np
from typing import List, Tuple


def exact_match_score(predictions: List[str], references: List[str]) -> float:
    """
    Calculate Exact Match (EM) score

    Args:
        predictions: List of predicted sentences
        references: List of reference (correct) sentences

    Returns:
        float: EM score (0-100)
    """
    if len(predictions) != len(references):
        raise ValueError("Predictions and references must have same length")

    matches = sum(1 for pred, ref in zip(predictions, references) if pred == ref)
    return (matches / len(predictions)) * 100


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein edit distance between two strings

    Args:
        s1: First string
        s2: Second string

    Returns:
        int: Edit distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertion, deletion, substitution
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def character_error_rate(s1: str, s2: str) -> float:
    """
    Calculate Character Error Rate (CER) between two strings
    """
    if not s1:
        return 0.0 if not s2 else 1.0
    return levenshtein_distance(s1, s2) / len(s1)


def word_error_rate(s1: str, s2: str) -> float:
    """
    Calculate Word Error Rate (WER) between two strings
    """
    w1 = s1.split()
    w2 = s2.split()

    if not w1:
        return 0.0 if not w2 else 1.0

    # Use levenshtein on words
    m, n = len(w1), len(w2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if w1[i-1] == w2[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)

    return dp[m][n] / m


def batch_cer(predictions: List[str], references: List[str]) -> float:
    """
    Calculate average CER over a batch
    """
    total_dist = 0
    total_len = 0
    for p, r in zip(predictions, references):
        total_dist += levenshtein_distance(p, r)
        total_len += len(r)
    return (total_dist / total_len) * 100 if total_len > 0 else 0.0


def batch_wer(predictions: List[str], references: List[str]) -> float:
    """
    Calculate average WER over a batch
    """
    total_wer = 0.0
    for p, r in zip(predictions, references):
        total_wer += word_error_rate(r, p)
    return (total_wer / len(references)) * 100 if references else 0.0


def word_level_metrics(predictions: List[List[str]],
                       references: List[List[str]],
                       error_flags: List[List[bool]]) -> Tuple[float, float, float]:
    """
    Calculate word-level Precision, Recall, F1

    Args:
        predictions: List of predicted word lists
        references: List of reference word lists
        error_flags: List of flags indicating which words had errors

    Returns:
        tuple: (precision, recall, f1)
    """
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for pred, ref, flags in zip(predictions, references, error_flags):
        for i, (p, r, flag) in enumerate(zip(pred, ref, flags)):
            if flag:  # This word had an error
                if p == r:
                    true_positives += 1
                else:
                    false_negatives += 1
            else:  # No error in original
                if p != r:
                    false_positives += 1

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return precision * 100, recall * 100, f1 * 100


# Placeholder for future implementations
def __init__():
    pass
