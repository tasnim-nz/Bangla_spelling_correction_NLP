"""
Phase 3: Noisy-Channel Model - Step 3
Candidate Generator via Edit Distance and Vocabulary Dictionary

This script:
1. Loads the Bangla vocabulary dictionary from Phase 1
2. Implements Damerau-Levenshtein edit distance
3. Generates correction candidates within edit distance 1 and 2
"""

import os
import sys
import json
from typing import List, Tuple, Dict, Set

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.io_utils import read_json

def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Damerau-Levenshtein distance between two strings.
    This includes insertions, deletions, substitutions, and transpositions.
    """
    m, n = len(s1), len(s2)
    # d[i][j] will store the DL distance between s1[:i] and s2[:j]
    d = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            d[i][j] = min(
                d[i-1][j] + 1,       # Deletion
                d[i][j-1] + 1,       # Insertion
                d[i-1][j-1] + cost,  # Substitution
            )
            # Transposition check
            if i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                d[i][j] = min(d[i][j], d[i-2][j-2] + 1)

    return d[m][n]

class CandidateGenerator:
    def __init__(self, vocab_file: str):
        """
        Initialize candidate generator by loading vocabulary.
        """
        self.vocab_file = vocab_file
        # Load vocabulary (can be list or dict)
        vocab_data = read_json(vocab_file)
        if isinstance(vocab_data, dict):
            self.vocabulary = set(vocab_data.keys())
        else:
            self.vocabulary = set(vocab_data)

        print(f"✓ Candidate Generator initialized with {len(self.vocabulary)} vocabulary words.")

    def generate_candidates(self, word: str, max_distance: int = 2) -> List[Tuple[str, int]]:
        """
        Generate correction candidates for a given word.
        Returns a list of (candidate, edit_distance) pairs.
        """
        if not word:
            return []

        # If word is in vocabulary, it's its own candidate with distance 0
        if word in self.vocabulary:
            return [(word, 0)]

        candidates = []
        for vocab_word in self.vocabulary:
            dist = damerau_levenshtein_distance(word, vocab_word)
            if dist <= max_distance:
                candidates.append((vocab_word, dist))

        # Sort candidates by distance first
        candidates.sort(key=lambda x: x[1])
        return candidates

if __name__ == "__main__":
    # Test Candidate Generator
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vocab_file = os.path.join(base_dir, "1_Data_Preprocessing", "outputs", "vocabulary.json")

    cg = CandidateGenerator(vocab_file)

    test_words = ["কোতি", "রাখ", "কড়া"]
    for w in test_words:
        candidates = cg.generate_candidates(w, max_distance=2)
        print(f"\nWord: {w}")
        print(f"Candidates (up to distance 2): {candidates[:10]}")
