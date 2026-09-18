# Phase 3: Noisy-Channel Model Implementation Plan

This phase implements a classical noisy-channel spelling corrector for Bangla.

## 1. `ngram_lm.py`
- **Purpose**: A wrapper for the n-gram language models built in Phase 1.
- **Functionality**:
  - Load `unigram_model.pkl`, `bigram_model.pkl`, and `trigram_model.pkl`.
  - Provide a function `get_sentence_probability(sentence)` that calculates the prior probability $P(c)$ of a candidate sentence using interpolation of n-grams.

## 2. `error_model.py`
- **Purpose**: Estimates $P(w|c)$, the probability that the correct word $c$ was mistyped as $w$.
- **Functionality**:
  - Load error pairs from `train_errors.jsonl`.
  - Build confusion matrices for character-level edits (insertions, deletions, substitutions, transpositions).
  - Calculate probabilities based on the frequency of these edits in the training data.
  - Handle cases for phonetic and visual errors specifically if possible, or treat them as general substitutions.

## 3. `candidate_generator.py`
- **Purpose**: Generates potential correction candidates for a misspelled word.
- **Functionality**:
  - Load the vocabulary from `vocabulary.json`.
  - Use edit distance (Damerau-Levenshtein) to find words in the vocabulary that are within a small distance (e.g., distance 1 or 2) from the input word.
  - Return a list of (candidate, score) pairs.

## 4. `build_nc_model.py`
- **Purpose**: Integrates the language model and error model.
- **Functionality**:
  - For a given erroneous word (or sentence), find candidates.
  - For each candidate $c$, calculate $Score(c) = P(c) \times P(w|c)$.
  - Return the candidate with the highest score.

## 5. `inference_nc.py`
- **Purpose**: Evaluate the noisy-channel model on the test set.
- **Functionality**:
  - Load `test_errors.jsonl`.
  - Run the corrector on each `corrupted` sentence.
  - Compare results with `original` sentences.
  - Calculate metrics: Word Error Rate (WER), Character Error Rate (CER), and Accuracy.
  - Save results and statistics to `3_Noisy_Channel_Model/outputs/`.

---

## File Structure for Phase 3
All files will be located in `Bananriti/3_Noisy_Channel_Model/`.

- `ngram_lm.py`
- `error_model.py`
- `candidate_generator.py`
- `nc_corrector.py` (Instead of `build_nc_model.py`, this will be the main class/utility)
- `inference_nc.py`
