"""
Phase 3: Noisy-Channel Model - Step 4
Noisy-Channel Spelling Corrector

This script combines:
1. Language Model (P(c))
2. Error Model (P(w|c))
3. Candidate Generator (edit distance candidates)

And implements the Noisy-Channel principle:
    argmax_c P(c|w) = argmax_c P(w|c) * P(c)
"""

import os
import sys
import math
from typing import List, Tuple, Dict, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ngram_lm import NgramLanguageModel
from error_model import ErrorModel
from candidate_generator import CandidateGenerator, damerau_levenshtein_distance
from utils.bangla_utils import tokenize_bangla_words
from utils.io_utils import read_json

class NoisyChannelCorrector:
    def __init__(self, model_dir: str, vocab_file: str,
                 train_corpus_file: str, train_errors_file: str):
        """
        Initialize the noisy-channel corrector.
        """
        print("Initializing Noisy-Channel Corrector...")

        # Load Language Model
        self.lm = NgramLanguageModel(model_dir)

        # Load Candidate Generator
        self.cg = CandidateGenerator(vocab_file)

        # Load Error Model
        self.em = ErrorModel(train_corpus_file, train_errors_file)

        print("✓ Noisy-Channel Corrector ready.")

    def correct_word(self, word: str, context: str = "") -> str:
        """
        Correct a single word using the noisy-channel principle.

        Args:
            word: The misspelled word
            context: The surrounding sentence context (for LM scoring)

        Returns:
            The most likely correct word.
        """
        # If word is in vocabulary, it's likely correct
        if word in self.cg.vocabulary:
            return word

        # Generate candidates
        candidates = self.cg.generate_candidates(word, max_distance=2)

        if not candidates:
            return word  # No candidates found, return original

        # Score each candidate
        best_candidate = word
        best_score = -float('inf')

        for cand, dist in candidates:
            # P(c): Language model probability of the candidate in context
            # We use the sentence with this word replaced by the candidate
            if context:
                sentence_with_cand = context.replace(word, cand)
            else:
                sentence_with_cand = cand

            p_c_log = self.lm.get_sentence_log_prob(sentence_with_cand)

            # P(w|c): Error model probability
            p_w_given_c = self.em.get_edit_probability(cand, word)
            p_w_given_c_log = math.log(p_w_given_c) if p_w_given_c > 0 else -float('inf')

            # Combined score: log P(w|c) + log P(c)
            score = p_w_given_c_log + p_c_log

            if score > best_score:
                best_score = score
                best_candidate = cand

        return best_candidate

    def correct_sentence(self, sentence: str) -> str:
        """
        Correct a full sentence word-by-word.

        Handles run-on and split-word errors by attempting to split/merge
        adjacent words if the individual words are not in vocabulary.
        """
        words = sentence.split()
        corrected_words = []

        for i, word in enumerate(words):
            # Check if word is in vocabulary
            if word in self.cg.vocabulary:
                corrected_words.append(word)
                continue

            # Try to correct as a single word
            corrected = self.correct_word(word, sentence)
            if corrected != word:
                corrected_words.append(corrected)
                continue

            # If single-word correction failed, try split-word correction:
            # The word might actually be two words merged with a space (run-on error).
            # Try inserting a space at each possible position.
            split_candidates = self._try_split_word(word)
            if split_candidates:
                # Use the first valid split (we could score them, but for simplicity)
                corrected_words.extend(split_candidates)
                continue

            # If still no correction, keep original
            corrected_words.append(word)

        return ' '.join(corrected_words)

    def _try_split_word(self, word: str) -> Optional[List[str]]:
        """
        Try to split a merged word into two valid vocabulary words.
        This handles run-on errors.
        """
        if len(word) < 4:
            return None

        # Try all possible split points
        for split_pos in range(1, len(word)):
            left_part = word[:split_pos]
            right_part = word[split_pos:]

            # Check if both parts are in vocabulary
            if left_part in self.cg.vocabulary and right_part in self.cg.vocabulary:
                return [left_part, right_part]

        return None

if __name__ == "__main__":
    # Test the corrector
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, "1_Data_Preprocessing", "outputs")
    vocab_file = os.path.join(base_dir, "1_Data_Preprocessing", "outputs", "vocabulary.json")
    train_corpus_file = os.path.join(base_dir, "1_Data_Preprocessing", "outputs", "train_corpus.txt")
    train_errors_file = os.path.join(base_dir, "2_Error_Generation", "outputs", "train_errors.jsonl")

    corrector = NoisyChannelCorrector(model_dir, vocab_file, train_corpus_file, train_errors_file)

    # Test cases
    test_sentences = [
        "কোতি ২০ রাখ গবাদিপশুর",  # corrupted version of কোটি ২০ লাখ গবাদিপশুর
        "গ্রামকিংবা শহরসব জায়গাতেই",  # run-on error
        "সরখারি-বেসরকারি",  # phonetic error
    ]

    for s in test_sentences:
        corrected = corrector.correct_sentence(s)
        print(f"\nOriginal: {s}")
        print(f"Corrected: {corrected}")