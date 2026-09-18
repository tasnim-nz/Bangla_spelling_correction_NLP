# বানানরীতি (BANANRITI)

**A Comparative Study of Noisy-Channel and BanglaT5 Models for Bangla Spelling Correction**

BANANRITI is an NLP project that compares a classical probabilistic spell checker with a transformer-based BanglaT5 model using a synthetic Bangla spelling correction dataset created from Bangla news text.

## Project Overview

Bangla spelling correction is challenging because text written in online and informal settings often contains phonetic substitutions, visually similar characters, keyboard errors, incorrect word boundaries, and run-on words. A robust correction system must use both the structure of the language and evidence from observed errors.

This project compares two approaches:

- **Classical Noisy Channel Model:** An interpretable probabilistic system using an n-gram language model, candidate generation, and a learned character-level error model.
- **BanglaT5 Transformer:** A context-aware sequence-to-sequence model intended for neural spelling correction.

The dataset is built from a Bangla news corpus and transformed into parallel clean-noisy sentence pairs using synthetic error patterns. This repository currently contains the complete classical noisy-channel pipeline through Phase 4.5. The BanglaT5 implementation is the next major stage of the project.

## Repository Structure

```text
Bangla_spelling_correction_NLP/
│
├── 1_Data_Preprocessing/
├── 2_Error_Generation/
├── 3_Noisy_Channel_Model/
├── 4_BanglaT5_Model/
├── 5_Evaluation/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── splits/
│   └── noisy/
├── resources/
├── models/
├── outputs/
├── requirements.txt
└── README.md
```

- `1_Data_Preprocessing/`: Collects, cleans, normalizes, and splits the Bangla corpus.
- `2_Error_Generation/`: Generates synthetic spelling errors and parallel clean-noisy data.
- `3_Noisy_Channel_Model/`: Contains the language model, error model, candidate generator, and inference engine.
- `4_BanglaT5_Model/`: Reserved for BanglaT5 data preparation, fine-tuning, and inference.
- `5_Evaluation/`: Evaluates model predictions and stores metrics and error-type results.
- `data/`: Stores raw, processed, split, and noisy datasets.
- `resources/`: Stores the dictionary and phonetic, visual, keyboard, and vocabulary resources.
- `models/`: Stores trained statistical model artifacts.
- `outputs/`: Stores predictions, metrics, and other experiment outputs.

## Completed Pipeline (Phase 1-4.5)

| Phase | Description | Status |
|---|---|---|
| Corpus Collection | Collect Bangla news text for the project corpus. | Completed |
| Preprocessing | Clean, normalize, and prepare the corpus. | Completed |
| Vocabulary Building | Build the Bangla vocabulary and frequency resources. | Completed |
| Dataset Split | Create training, validation, and test corpus splits. | Completed |
| Synthetic Error Generation | Generate clean-noisy sentence pairs across five error categories. | Completed |
| N-gram Language Model | Build smoothed unigram and bigram language models. | Completed |
| Candidate Generation | Generate spelling candidates using edit and confusion resources. | Completed |
| Error Model | Learn character confusion probabilities from synthetic pairs. | Completed |
| Noisy Channel Inference | Decode corrections with confidence, punctuation, split, and run-on handling. | Completed |
| Evaluation | Evaluate the classical model on the held-out test set. | Completed |

## Dataset Summary

| Item | Value |
|---|---:|
| Raw corpus sentences | 10,000 |
| Clean corpus sentences | 9,812 |
| Train sentences | 6,868 |
| Validation sentences | 981 |
| Test sentences | 1,963 |
| Total noisy-clean pairs | 49,060 |
| Vocabulary size | 16,069 |

The noisy dataset contains five synthetic error categories: phonetic, visual, keyboard, split, and run-on errors.

## Synthetic Error Types

| Error Type | Description | Example |
|---|---|---|
| Phonetic | Similar pronunciation | বাংলাদেস → বাংলাদেশ |
| Visual | Similar-looking letters | ভাংলাদেশ → বাংলাদেশ |
| Keyboard | Neighboring keyboard characters | লাইণে → লাইনে |
| Split | Incorrect word split | বাংলা দেশ → বাংলাদেশ |
| Run-on | Missing space | বাংলাদেশসরকার → বাংলাদেশ সরকার |

## Classical Noisy Channel Model

### Language Model

- Unigram counts estimate individual word probabilities.
- Bigram counts model local word context.
- Laplace smoothing assigns non-zero probabilities to unseen words and word pairs.

### Candidate Generator

Candidates are generated using:

- Edit Distance 1
- Edit Distance 2
- Phonetic confusion map
- Visual confusion map
- Keyboard confusion map

### Error Model

The error model estimates character confusion probabilities learned from synthetic noisy-clean sentence pairs.

### Inference

The inference engine performs noisy-channel decoding and includes:

- A confidence threshold for conservative correction.
- Dictionary preservation for already-correct words.
- Punctuation preservation for attached punctuation.
- Split-error handling for concatenated dictionary words.
- Run-on handling for adjacent tokens that form a dictionary word.

## Baseline Evaluation Results

| Metric | Result |
|---|---:|
| Test sentence pairs | 9,815 |
| Sentence Accuracy | **37.39%** |
| Word Accuracy | **86.79%** |
| Correction Accuracy | **66.12%** |

### Error-Type Accuracy

| Error Type | Accuracy |
|---|---:|
| Phonetic | 15.35% |
| Visual | 17.06% |
| Keyboard | 10.85% |
| Split | 80.89% |
| Run-on | 62.49% |

These results serve as the classical baseline for comparison with BanglaT5.

## How to Run

### Step 1: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment before continuing.

On Windows:

```powershell
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### Step 2: Install Requirements

```bash
pip install -r requirements.txt
```

### Step 3: Run Preprocessing

```bash
python 1_Data_Preprocessing/download_corpus.py
python 1_Data_Preprocessing/preprocess.py
python 1_Data_Preprocessing/build_vocabulary.py
python 1_Data_Preprocessing/split_corpus.py
```

### Step 4: Generate the Noisy Dataset

```bash
python 2_Error_Generation/error_generator.py
```

### Step 5: Build the Classical Model

```bash
python 3_Noisy_Channel_Model/ngram_lm.py
python 3_Noisy_Channel_Model/error_model.py
```

### Step 6: Run Inference

```bash
python 3_Noisy_Channel_Model/inference_nc.py
```

### Step 7: Evaluate

```bash
python 5_Evaluation/evaluate_noisy_channel.py
```

## Current Progress

- Phase 1 Complete
- Phase 2 Complete
- Phase 3 Complete
- Phase 4 Complete
- Phase 4.5 Evaluation Complete
- Phase 5 BanglaT5 Fine-tuning
- Phase 6 Model Comparison
- Phase 7 Final Report & Presentation

## Future Work

- Fine-tune BanglaT5.
- Compare BanglaT5 against the Noisy Channel baseline.
- Analyze correction quality by error type.
- Prepare IEEE-style experimental results.

## Contributors

| Contributor | GitHub Username |
|---|---|
| Contributor 1 | `@username1` |
| Contributor 2 | `@username2` |
| Contributor 3 | `@username3` |
