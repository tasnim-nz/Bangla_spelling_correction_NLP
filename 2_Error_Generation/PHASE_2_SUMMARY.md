# PHASE 2 COMPLETION SUMMARY
# Synthetic Error Generation for বানানরীতি (Bananriti)

## Phase 2: Synthetic Error Generation
**Status**: ✓ COMPLETE
**Date**: September 18, 2026

---

## 📋 What Was Accomplished

### Goal
Generate realistic synthetic Bangla spelling errors from the clean corpus
(Phase 1) to create parallel (erroneous → correct) training data for both
the Noisy-Channel Model (Phase 3) and BanglaT5 (Phase 4).

### Pipeline
1. Load clean train/val/test corpora from Phase 1
2. For each sentence, randomly select ~15% of words to corrupt
3. Apply one of 5 error types per selected word
4. Save parallel pairs (corrupted ↔ correct)

---

## 📊 Results

| Metric                      | Value |
|-----------------------------|-------|
| **Total parallel pairs**    | 334   |
| **Total errors injected**   | 718   |
| **Avg errors per sentence** | 2.15  |
| **Max errors in one sentence** | 3  |

### Split Sizes
| Split       | Pairs | Variants per sentence |
|-------------|-------|-----------------------|
| Train       | 274   | 2                     |
| Validation  | 19    | 1                     |
| Test        | 41    | 1                     |

### Error Type Distribution
| Error Type       | Count | Percentage |
|------------------|-------|------------|
| Typographical    | 258   | 35.9%      |
| Phonetic         | 226   | 31.5%      |
| Visual           | 153   | 21.3%      |
| Split-word       | 44    | 6.1%       |
| Run-on           | 37    | 5.2%       |

---

## 📂 Files Created

### Scripts (2 files)
- ✓ `error_patterns.py` — Error type definitions, phonetic/visual/keyboard maps
- ✓ `error_generator.py` — Main error injection pipeline

### Output Data (7 files)
- ✓ `outputs/train_errors.jsonl` — 274 pairs (detailed with error metadata)
- ✓ `outputs/val_errors.jsonl` — 19 pairs
- ✓ `outputs/test_errors.jsonl` — 41 pairs
- ✓ `outputs/train_parallel.tsv` — Tab-separated (corrupted ↔ correct)
- ✓ `outputs/val_parallel.tsv` — Tab-separated
- ✓ `outputs/test_parallel.tsv` — Tab-separated
- ✓ `outputs/error_generation_stats.json` — Generation statistics

---

## 🔍 Error Type Details

### 1. Phonetic Errors (31.5%)
Similar-sounding character substitutions based on Bangla phonology:
- Dental ↔ Retroflex: ত↔ট, দ↔ড, ধ↔ঢ, ন↔ণ
- Sibilants: শ↔ষ↔স
- Aspirated pairs: ক↔খ, গ↔ঘ, চ↔ছ, প↔ফ, ব↔ভ
- Flaps: ড়↔র

### 2. Visual Errors (21.3%)
Characters that look alike in common Bangla fonts:
- Consonants: ব↔য়, ক↔খ, ত↔থ, ড↔ড়
- Vowel signs: ি↔ী, ু↔ূ, ে↔ৈ, ো↔ৌ

### 3. Typographical Errors (35.9%)
Four sub-operations:
- **Substitution (30%)**: Replace with keyboard-neighbour character
- **Insertion (25%)**: Extra random Bangla character inserted
- **Deletion (25%)**: One character removed
- **Transposition (20%)**: Two adjacent characters swapped

### 4. Split-word Errors (6.1%)
A space inserted inside a word (minimum 5 characters), splitting it into
two fragments.

### 5. Run-on Errors (5.2%)
Space between two consecutive words removed, merging them into one token.

---

## 📝 Sample Error Pairs

| # | Original | Corrupted | Error Type |
|---|----------|-----------|------------|
| 1 | কোটি → কোতি | phonetic: ট→ত |
| 2 | লাখ → রাখ | typo-sub: ল→র |
| 3 | করা → কড়া | phonetic: র→ড় |
| 4 | কোরবানি → কোরবানী | visual: ি→ী |
| 5 | সঙ্গে মহিষটিকেও → সঙ্গেমহিষটিকেও | run-on |

---

## ⚙️ Configuration

- **Random seed**: 42 (reproducible)
- **Error rate per sentence**: ~15% of words
- **Max errors per sentence**: 3
- **Min word length for error**: 3 characters
- **Train variants per sentence**: 2
- **Val/Test variants per sentence**: 1

---

## 📋 Data Format

### JSONL Format (detailed)
```json
{
  "original": "গ্রাম কিংবা শহরসব জায়গাতেই মানুষের সাথে বিড়াল বাস করতে পছন্দ করে",
  "corrupted": "গ্রামকিংবা শহরসব জায়গাতেই মানুষের সাথে বিড়াল বাস করতে পজন্দ করে",
  "errors": [
    {
      "word_index": 0,
      "original_word": "গ্রাম কিংবা",
      "corrupted_word": "গ্রামকিংবা",
      "error_type": "run_on",
      "description": "run-on: merged words at pos 0 and 1"
    }
  ]
}
```

### TSV Format (simple)
```
corrupted	correct
গ্রামকিংবা শহরসব জায়গাতেই ...	গ্রাম কিংবা শহরসব জায়গাতেই ...
```

---

## ✅ Phase 2 Verification Checklist

- ✓ Error patterns module created with comprehensive maps
- ✓ All 5 error types implemented and functional
- ✓ Error distribution matches configured weights
- ✓ Parallel pairs generated for train/val/test splits
- ✓ JSONL with full error metadata saved
- ✓ TSV with simple parallel format saved
- ✓ Statistics computed and saved
- ✓ Reproducible (seed = 42)
- ✓ All files saved with UTF-8 encoding

---

## 🚀 Next Steps: Phase 3 — Noisy-Channel Model

Phase 3 will build the classical spelling corrector:

1. **`ngram_lm.py`** — Load unigram/bigram/trigram language models from Phase 1
2. **`error_model.py`** — Build P(error|correct) from Phase 2 error pairs
3. **`candidate_generator.py`** — Generate correction candidates via edit distance + dictionary
4. **`build_nc_model.py`** — Combine language model + error model (Noisy-Channel)
5. **`inference_nc.py`** — Run spelling correction on test set

### Data Flow
```
Phase 1 outputs (LM + vocabulary) ─┐
                                     ├──→ Phase 3: Noisy-Channel Model
Phase 2 outputs (error pairs)     ──┘
```

---

**Project**: বানানরীতি (Bananriti) — Bangla Spelling Error Correction
**Status**: Phase 2 Complete ✓
**Next**: Phase 3 — Noisy-Channel Model
**Date**: September 18, 2026
