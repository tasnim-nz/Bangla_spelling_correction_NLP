"""
Phase 3: Noisy-Channel Model - Step 5
Inference and Evaluation on Test Set

This script:
1. Loads the test error pairs from Phase 2
2. Runs the noisy-channel corrector on each corrupted sentence
3. Compares corrected sentences with the ground truth
4. Calculates metrics: Word Error Rate (WER), Character Error Rate (CER), Accuracy
5. Saves detailed results and summary statistics
"""

import os
import sys
import json
import time
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nc_corrector import NoisyChannelCorrector
from utils.io_utils import read_jsonl, write_json, write_jsonl
from utils.metrics import word_error_rate, character_error_rate

def load_test_data(test_file: str) -> List[Dict]:
    """Load test error pairs."""
    return read_jsonl(test_file)

def evaluate_corrector(corrector: NoisyChannelCorrector, test_data: List[Dict]) -> Dict:
    """
    Run corrector on test data and compute evaluation metrics.
    """
    total_pairs = len(test_data)
    total_words_original = 0
    total_words_corrected = 0

    total_wer = 0.0
    total_cer = 0.0
    exact_match_count = 0

    results = []

    print(f"\nEvaluating on {total_pairs} test pairs...")
    start_time = time.time()

    for idx, pair in enumerate(test_data, 1):
        corrupted = pair['corrupted']
        original = pair['original']

        # Run correction
        corrected = corrector.correct_sentence(corrupted)

        # Calculate metrics
        wer = word_error_rate(original, corrected)
        cer = character_error_rate(original, corrected)

        # Exact match check
        exact_match = (original == corrected)

        results.append({
            'index': idx,
            'corrupted': corrupted,
            'corrected': corrected,
            'original': original,
            'wer': round(wer, 4),
            'cer': round(cer, 4),
            'exact_match': exact_match,
            'errors': pair.get('errors', [])
        })

        total_wer += wer
        total_cer += cer
        if exact_match:
            exact_match_count += 1

        total_words_original += len(original.split())
        total_words_corrected += len(corrected.split())

        if idx % 10 == 0:
            print(f"  Processed {idx}/{total_pairs} pairs...")

    elapsed = time.time() - start_time

    # Calculate averages
    avg_wer = total_wer / total_pairs if total_pairs > 0 else 0.0
    avg_cer = total_cer / total_pairs if total_pairs > 0 else 0.0
    exact_match_rate = exact_match_count / total_pairs if total_pairs > 0 else 0.0

    stats = {
        'total_pairs': total_pairs,
        'exact_match_count': exact_match_count,
        'exact_match_rate': round(exact_match_rate, 4),
        'avg_word_error_rate': round(avg_wer, 4),
        'avg_character_error_rate': round(avg_cer, 4),
        'total_words_original': total_words_original,
        'total_words_corrected': total_words_corrected,
        'processing_time_seconds': round(elapsed, 2),
        'processing_time_per_pair_seconds': round(elapsed / total_pairs, 4) if total_pairs > 0 else 0.0
    }

    return stats, results

def main():
    print("=" * 70)
    print("PHASE 3: NOISY-CHANNEL MODEL INFERENCE & EVALUATION")
    print("=" * 70)

    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, "1_Data_Preprocessing", "outputs")
    vocab_file = os.path.join(base_dir, "1_Data_Preprocessing", "outputs", "vocabulary.json")
    train_corpus_file = os.path.join(base_dir, "1_Data_Preprocessing", "outputs", "train_corpus.txt")
    train_errors_file = os.path.join(base_dir, "2_Error_Generation", "outputs", "train_errors.jsonl")
    test_file = os.path.join(base_dir, "2_Error_Generation", "outputs", "test_errors.jsonl")

    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Load corrector
    print("\n[1/4] Initializing Noisy-Channel Corrector...")
    corrector = NoisyChannelCorrector(model_dir, vocab_file, train_corpus_file, train_errors_file)

    # Load test data
    print("\n[2/4] Loading test data...")
    test_data = load_test_data(test_file)
    print(f"✓ Loaded {len(test_data)} test pairs")

    # Evaluate
    print("\n[3/4] Running inference and evaluation...")
    stats, results = evaluate_corrector(corrector, test_data)

    # Save results
    print("\n[4/4] Saving results...")
    write_json(os.path.join(output_dir, "outputs", "nc_evaluation_stats.json"), stats)
    write_jsonl(os.path.join(output_dir, "outputs", "nc_evaluation_results.jsonl"), results)

    # Print summary
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Test Pairs         : {stats['total_pairs']}")
    print(f"Exact Match Count         : {stats['exact_match_count']}")
    print(f"Exact Match Rate          : {stats['exact_match_rate']:.2%}")
    print(f"Average Word Error Rate   : {stats['avg_word_error_rate']:.4f}")
    print(f"Average Character Error Rate : {stats['avg_character_error_rate']:.4f}")
    print(f"Total Words (Original)    : {stats['total_words_original']}")
    print(f"Total Words (Corrected)   : {stats['total_words_corrected']}")
    print(f"Processing Time           : {stats['processing_time_seconds']:.2f}s")
    print(f"Time per Pair             : {stats['processing_time_per_pair_seconds']:.4f}s")
    print("=" * 70)

    # Show some examples
    print("\n" + "-" * 70)
    print("SAMPLE CORRECTIONS (first 10)")
    print("-" * 70)
    for r in results[:10]:
        print(f"\nPair {r['index']}:")
        print(f"  Corrupted : {r['corrupted']}")
        print(f"  Corrected : {r['corrected']}")
        print(f"  Original  : {r['original']}")
        print(f"  WER: {r['wer']:.4f} | CER: {r['cer']:.4f} | Exact Match: {r['exact_match']}")

    print("\n✓ Phase 3 Inference Complete!")
    print(f"✓ Results saved to: {os.path.join(output_dir, 'outputs')}")

if __name__ == "__main__":
    main()