"""
Phase 3: Noisy-Channel Model - Step 2
Error Model P(w|c) using Confusion Matrices and Edit Distance

This script:
1. Loads training error pairs from Phase 2
2. Computes character and bigram frequencies from the clean training corpus
3. Aligns erroneous words with correct words using Damerau-Levenshtein distance
4. Builds confusion matrices for insert, delete, substitute, and transpose edits
5. Calculates P(w|c) for correction candidates
"""

import os
import sys
import json
from collections import defaultdict, Counter
import math
from typing import List, Tuple, Dict, Set, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bangla_utils import tokenize_bangla_words
from utils.io_utils import read_lines, read_jsonl

class ErrorModel:
    def __init__(self, train_corpus_file: str, train_errors_file: str):
        """
        Initialize and train the error model using a clean training corpus
        and parallel training error pairs.
        """
        self.train_corpus_file = train_corpus_file
        self.train_errors_file = train_errors_file

        # Initialize confusion matrices
        # Format:
        # ins_matrix[x][y] = count(x -> xy)  - y is inserted after x
        # del_matrix[x][y] = count(xy -> x)  - y is deleted after x
        # sub_matrix[x][y] = count(x -> y)   - x is substituted by y
        # trans_matrix[x][y] = count(xy -> yx) - xy is transposed to yx
        self.ins_matrix = defaultdict(Counter)
        self.del_matrix = defaultdict(Counter)
        self.sub_matrix = defaultdict(Counter)
        self.trans_matrix = defaultdict(Counter)

        # Base character and bigram frequencies in clean corpus
        self.char_counts = Counter()
        self.bigram_counts = Counter()
        self.total_chars = 0

        # Build counts and confusion matrices
        self._calculate_corpus_statistics()
        self._build_confusion_matrices()

    def _calculate_corpus_statistics(self):
        """Calculate single character and character bigram frequencies from clean corpus."""
        print("Calculating character and bigram frequencies from clean training corpus...")
        sentences = read_lines(self.train_corpus_file)

        for sentence in sentences:
            # We want character level counts, keeping spaces as characters to handle split/run-on if needed
            # For simplicity, we process each line as-is
            line = sentence.strip()
            if not line:
                continue

            self.total_chars += len(line)
            for i, ch in enumerate(line):
                self.char_counts[ch] += 1
                if i > 0:
                    prev_ch = line[i-1]
                    self.bigram_counts[(prev_ch, ch)] += 1

        print(f"✓ Processed {len(sentences)} clean sentences.")
        print(f"✓ Found {len(self.char_counts)} unique characters and {len(self.bigram_counts)} unique bigrams.")

    def _align_words(self, correct: str, corrupted: str) -> List[Tuple[str, str, str]]:
        """
        Damerau-Levenshtein alignment to extract edit operations.
        Returns a list of edits: (op_type, correct_char(s), corrupted_char(s))
        where op_type can be: 'match', 'sub', 'ins', 'del', 'trans'
        """
        m, n = len(correct), len(corrupted)

        # dp[i][j] holds the minimum edit distance between correct[:i] and corrupted[:j]
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        # track backpointers to reconstruct path
        # backpointer structure: (prev_i, prev_j, op_name, arg1, arg2)
        bp = [[None] * (n + 1) for _ in range(m + 1)]

        # Base cases
        for i in range(m + 1):
            dp[i][0] = i
            if i > 0:
                prev_char = correct[i-2] if i > 1 else '^'
                bp[i][0] = (i - 1, 0, 'del', prev_char, correct[i-1]) # delete correct[i-1] after correct[i-2]

        for j in range(n + 1):
            dp[0][j] = j
            if j > 0:
                prev_char = '^' # boundary symbol
                bp[0][j] = (0, j - 1, 'ins', prev_char, corrupted[j-1]) # insert corrupted[j-1] after boundary

        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                c_char = correct[i-1]
                w_char = corrupted[j-1]

                # Match or Substitution
                cost = 0 if c_char == w_char else 1
                best_cost = dp[i-1][j-1] + cost
                op = 'match' if cost == 0 else 'sub'
                prev_i, prev_j = i-1, j-1
                arg1, arg2 = c_char, w_char

                # Deletion
                if dp[i-1][j] + 1 < best_cost:
                    best_cost = dp[i-1][j] + 1
                    op = 'del'
                    prev_i, prev_j = i-1, j
                    arg1 = correct[i-2] if i > 1 else '^'
                    arg2 = correct[i-1]

                # Insertion
                if dp[i][j-1] + 1 < best_cost:
                    best_cost = dp[i][j-1] + 1
                    op = 'ins'
                    prev_i, prev_j = i, j-1
                    arg1 = correct[i-1] if i > 0 else '^'
                    arg2 = corrupted[j-1]

                # Transposition (Damerau-Levenshtein)
                if i > 1 and j > 1 and correct[i-1] == corrupted[j-2] and correct[i-2] == corrupted[j-1]:
                    if dp[i-2][j-2] + 1 < best_cost:
                        best_cost = dp[i-2][j-2] + 1
                        op = 'trans'
                        prev_i, prev_j = i-2, j-2
                        arg1 = correct[i-2]
                        arg2 = correct[i-1]

                dp[i][j] = best_cost
                bp[i][j] = (prev_i, prev_j, op, arg1, arg2)

        # Backtrack to find edits
        edits = []
        i, j = m, n
        while bp[i][j] is not None:
            prev_i, prev_j, op, arg1, arg2 = bp[i][j]
            if op != 'match':
                edits.append((op, arg1, arg2))
            i, j = prev_i, prev_j

        return edits[::-1] # return in chronological order

    def _build_confusion_matrices(self):
        """Build confusion matrices from the training error pairs."""
        print("Building confusion matrices from training errors...")
        error_pairs = read_jsonl(self.train_errors_file)

        pair_count = 0
        edit_count = 0

        for item in error_pairs:
            # We process individual word errors reported in Phase 2
            for err in item.get('errors', []):
                # skip split_word and run_on errors as they are handled differently
                if err['error_type'] in ('split_word', 'run_on'):
                    continue

                correct_word = err['original_word']
                corrupted_word = err['corrupted_word']

                # Perform character alignment
                edits = self._align_words(correct_word, corrupted_word)
                for op, x, y in edits:
                    if op == 'sub':
                        self.sub_matrix[x][y] += 1
                    elif op == 'ins':
                        self.ins_matrix[x][y] += 1
                    elif op == 'del':
                        self.del_matrix[x][y] += 1
                    elif op == 'trans':
                        self.trans_matrix[x][y] += 1
                    edit_count += 1

                pair_count += 1

        print(f"✓ Processed {pair_count} error pairs.")
        print(f"✓ Extracted {edit_count} char-level edit operations.")

    def get_edit_probability(self, correct: str, corrupted: str) -> float:
        """
        Calculate P(w|c) based on Kernighan's confusion matrix formula.
        If words are identical, return a high probability.
        If words differ by more than edit distance 2, return 0.0 (or extremely low).
        """
        if correct == corrupted:
            # Match probability: typically ~0.95 or estimated from training
            return 0.95

        edits = self._align_words(correct, corrupted)
        if not edits:
            return 0.00001

        # If there are more than 2 edits, return near-zero
        if len(edits) > 2:
            return 1e-10

        prob = 1.0
        # Calculate joint probability of edits assuming independence (standard simplifcation)
        for op, x, y in edits:
            edit_prob = 1e-6 # Default low probability for unseen edits (Laplace / Add-epsilon smoothing)

            if op == 'sub':
                # P(x -> y) = count(sub(x,y)) / count(x)
                denom = self.char_counts[x]
                if denom > 0:
                    count = self.sub_matrix[x].get(y, 0)
                    edit_prob = (count + 0.1) / (denom + 0.1 * len(self.char_counts))

            elif op == 'ins':
                # P(x -> xy) = count(ins(x,y)) / count(x)
                denom = self.char_counts[x]
                if denom > 0:
                    count = self.ins_matrix[x].get(y, 0)
                    edit_prob = (count + 0.1) / (denom + 0.1 * len(self.char_counts))

            elif op == 'del':
                # P(xy -> x) = count(del(x,y)) / count(xy)
                denom = self.bigram_counts.get((x, y), 0)
                if denom == 0:
                    denom = self.char_counts[x] # Fallback
                if denom > 0:
                    count = self.del_matrix[x].get(y, 0)
                    edit_prob = (count + 0.1) / (denom + 0.1 * len(self.char_counts))

            elif op == 'trans':
                # P(xy -> yx) = count(trans(x,y)) / count(xy)
                denom = self.bigram_counts.get((x, y), 0)
                if denom > 0:
                    count = self.trans_matrix[x].get(y, 0)
                    edit_prob = (count + 0.1) / (denom + 0.1 * len(self.char_counts))

            prob *= edit_prob

        return prob

if __name__ == "__main__":
    # Test the error model
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_corpus = os.path.join(base_dir, "1_Data_Preprocessing", "outputs", "train_corpus.txt")
    train_errors = os.path.join(base_dir, "2_Error_Generation", "outputs", "train_errors.jsonl")

    em = ErrorModel(train_corpus, train_errors)

    # Test alignment
    print("\nTesting Alignment:")
    test_cases = [
        ("লাখ", "রাখ"),
        ("করা", "কড়া"),
        ("কোটি", "কোতি")
    ]
    for corr, corr_err in test_cases:
        edits = em._align_words(corr, corr_err)
        prob = em.get_edit_probability(corr, corr_err)
        print(f"Correct: {corr} | Corrupted: {corr_err} | Edits: {edits} | P(w|c): {prob:.6f}")
