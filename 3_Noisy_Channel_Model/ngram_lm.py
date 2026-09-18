"""
Phase 3: Noisy-Channel Model - Step 1
N-gram Language Model Wrapper

This script loads the pre-trained n-gram models and calculates
sentence probabilities P(c).
"""

import os
import sys
import math
import pickle
from typing import List, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bangla_utils import tokenize_bangla_words
from utils.io_utils import load_pickle

class NgramLanguageModel:
    def __init__(self, model_dir: str):
        """
        Initialize the language model by loading saved pickles.
        """
        print(f"Loading language models from {model_dir}...")

        self.unigram_model = load_pickle(os.path.join(model_dir, "unigram_model.pkl"))
        self.bigram_model = load_pickle(os.path.join(model_dir, "bigram_model.pkl"))
        self.trigram_model = load_pickle(os.path.join(model_dir, "trigram_model.pkl"))

        self.vocab_size = len(self.unigram_model)
        print(f"✓ Language models loaded (Vocab size: {self.vocab_size})")

    def get_word_prob(self, word: str) -> float:
        """Get unigram probability with backoff to small value."""
        return self.unigram_model.get(word, 1.0 / (self.vocab_size * 100))

    def get_sentence_log_prob(self, sentence: str) -> float:
        """
        Calculate log probability of a sentence using interpolation.
        P(w_i) = λ1*P(w_i|w_{i-2},w_{i-1}) + λ2*P(w_i|w_{i-1}) + λ3*P(w_i)
        """
        words = tokenize_bangla_words(sentence)
        words = ['<START>', '<START>'] + words + ['<END>']

        log_prob = 0.0

        # Interpolation weights
        l1, l2, l3 = 0.5, 0.3, 0.2

        for i in range(2, len(words)):
            w1, w2, w3 = words[i-2], words[i-1], words[i]

            # Trigram probability
            p3 = 0.0
            if (w1, w2) in self.trigram_model and w3 in self.trigram_model[(w1, w2)]:
                p3 = self.trigram_model[(w1, w2)][w3]

            # Bigram probability
            p2 = 0.0
            if (w2,) in self.bigram_model and w3 in self.bigram_model[(w2,)]:
                p2 = self.bigram_model[(w2,)][w3]

            # Unigram probability
            p1 = self.get_word_prob(w3)

            # Interpolated probability
            prob = l1 * p3 + l2 * p2 + l3 * p1

            if prob > 0:
                log_prob += math.log(prob)
            else:
                log_prob += -100.0 # Very low probability for unseen transitions

        return log_prob

if __name__ == "__main__":
    # Test the model
    model_dir = os.path.join("..", "1_Data_Preprocessing", "outputs")
    lm = NgramLanguageModel(model_dir)

    test_sentences = [
        "আমি ভাত খাই",
        "সে স্কুলে যায়",
        "বাংলার সংস্কৃতি অত্যন্ত সমৃদ্ধ"
    ]

    for s in test_sentences:
        lp = lm.get_sentence_log_prob(s)
        print(f"Sentence: {s} | LogProb: {lp:.4f}")
