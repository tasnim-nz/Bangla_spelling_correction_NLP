# PHASE 0 SETUP COMPLETE
# Project Structure Initialization for বানানরীতি (Bananriti)

## Phase 0: Project Structure & Environment Setup
**Status**: ✓ COMPLETE
**Date**: September 17, 2026
**Time**: 17:37 UTC

---

## 📂 Project Folder Structure Created

```
Bananriti/
├── 1_Data_Preprocessing/
│   ├── __init__.py
│   ├── outputs/                    [Folder for Phase 1 outputs]
│   ├── download_corpus.py          [To be created in Phase 1]
│   ├── preprocess.py               [To be created in Phase 1]
│   └── split_corpus.py             [To be created in Phase 1]
│
├── 2_Error_Generation/
│   ├── __init__.py
│   ├── outputs/                    [Folder for Phase 2 outputs]
│   ├── error_generator.py          [To be created in Phase 2]
│   └── error_patterns.py           [To be created in Phase 2]
│
├── 3_Noisy_Channel_Model/
│   ├── __init__.py
│   ├── outputs/                    [Folder for Phase 3 outputs]
│   ├── build_nc_model.py           [To be created in Phase 3]
│   ├── ngram_lm.py                 [To be created in Phase 3]
│   ├── error_model.py              [To be created in Phase 3]
│   ├── candidate_generator.py      [To be created in Phase 3]
│   └── inference_nc.py             [To be created in Phase 3]
│
├── 4_BanglaT5_Model/
│   ├── __init__.py
│   ├── configs/                    [Training configuration folder]
│   ├── outputs/                    [Folder for Phase 4 outputs]
│   ├── prepare_data.py             [To be created in Phase 4]
│   ├── fine_tune.py                [To be created in Phase 4]
│   └── inference_t5.py             [To be created in Phase 4]
│
├── 5_Evaluation/
│   ├── __init__.py
│   ├── outputs/                    [Folder for Phase 5 outputs]
│   ├── evaluate.py                 [To be created in Phase 5]
│   ├── compare_models.py           [To be created in Phase 5]
│   ├── error_analysis.py           [To be created in Phase 5]
│   └── visualize_results.py        [To be created in Phase 5]
│
├── resources/
│   ├── keyboard_maps/              [Keyboard layout mappings]
│   ├── bangla_dictionary.txt       [To be added]
│   ├── phonetic_map.json           [To be added]
│   └── visual_map.json             [To be added]
│
├── utils/
│   ├── __init__.py
│   ├── bangla_utils.py             [Bangla text utilities]
│   ├── metrics.py                  [Evaluation metrics]
│   ├── io_utils.py                 [File I/O operations]
│   └── visualization.py            [Plotting functions]
│
├── config.py                       [Project configuration & constants]
├── requirements.txt                [Python dependencies]
├── setup_environment.sh            [Unix/Linux setup script]
├── setup_environment.bat           [Windows setup script]
├── README.md                       [Project documentation]
└── PHASE_0_SUMMARY.md             [This file]
```

---

## ✓ Files Created in Phase 0

### Core Configuration Files
- ✓ `requirements.txt` - All Python dependencies
- ✓ `config.py` - Project constants and configuration
- ✓ `README.md` - Complete project documentation

### Setup Scripts
- ✓ `setup_environment.sh` - Unix/Linux setup
- ✓ `setup_environment.bat` - Windows setup

### Utility Modules (utils/)
- ✓ `utils/bangla_utils.py` - Bangla text processing functions
- ✓ `utils/metrics.py` - Evaluation metrics (EM, CER, F1, etc.)
- ✓ `utils/io_utils.py` - File I/O operations (JSON, pickle, text)
- ✓ `utils/visualization.py` - Plotting and chart functions

### Phase Initialization Files
- ✓ `1_Data_Preprocessing/__init__.py`
- ✓ `2_Error_Generation/__init__.py`
- ✓ `3_Noisy_Channel_Model/__init__.py`
- ✓ `4_BanglaT5_Model/__init__.py`
- ✓ `5_Evaluation/__init__.py`

### Output Folders (All Created)
- ✓ `1_Data_Preprocessing/outputs/`
- ✓ `2_Error_Generation/outputs/`
- ✓ `3_Noisy_Channel_Model/outputs/`
- ✓ `4_BanglaT5_Model/outputs/`
- ✓ `5_Evaluation/outputs/`
- ✓ `4_BanglaT5_Model/configs/`
- ✓ `resources/`
- ✓ `resources/keyboard_maps/`

---

## 📦 Dependencies Included in requirements.txt

### Deep Learning & ML
- torch==2.0.1
- torchvision==0.15.2
- torchaudio==2.0.2

### Transformers & NLP
- transformers==4.35.0
- datasets==2.14.0
- accelerate==0.25.0
- tokenizers==0.14.0
- nltk==3.8.1

### Data Processing
- numpy==1.24.3
- pandas==2.0.3
- scipy==1.11.0
- scikit-learn==1.3.0

### Visualization
- matplotlib==3.7.2
- seaborn==0.12.2

### Utilities
- tqdm==4.66.1
- python-dotenv==1.0.0
- pyyaml==6.0

---

## 🚀 Quick Start Guide

### On Windows:
```bash
# Navigate to project folder
cd Bananriti

# Run setup script (double-click or command line)
setup_environment.bat

# Activate virtual environment
venv\Scripts\activate
```

### On Mac/Linux:
```bash
# Navigate to project folder
cd Bananriti

# Make script executable
chmod +x setup_environment.sh

# Run setup script
./setup_environment.sh

# Activate virtual environment
source venv/bin/activate
```

### Manual Setup:
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

---

## 📋 Utility Modules Summary

### bangla_utils.py
Functions for Bangla text processing:
- `normalize_bangla_text()` - Unicode NFC normalization
- `is_bangla_character()` - Check if character is Bangla
- `is_bangla_word()` - Check if word is Bangla
- `remove_non_bangla()` - Remove non-Bangla characters
- `tokenize_bangla_words()` - Word-level tokenization
- `tokenize_bangla_chars()` - Character-level tokenization

### metrics.py
Evaluation metrics for spelling correction:
- `exact_match_score()` - EM score (0-100%)
- `levenshtein_distance()` - Edit distance calculation
- `character_error_rate()` - CER percentage
- `word_level_metrics()` - Precision, Recall, F1

### io_utils.py
File I/O operations:
- `read_text_file()` / `write_text_file()` - Text files
- `read_lines()` / `write_lines()` - Line-based I/O
- `read_json()` / `write_json()` - JSON files
- `read_jsonl()` / `write_jsonl()` - JSONL format
- `save_pickle()` / `load_pickle()` - Pickle serialization

### visualization.py
Plotting functions:
- `plot_confusion_matrix()` - Confusion matrices
- `plot_metrics_comparison()` - Model comparison charts
- `plot_error_distribution()` - Pie charts
- `plot_training_curves()` - Loss curves

---

## ⚙️ Configuration Included in config.py

### Project Metadata
- PROJECT_NAME, DESCRIPTION, VERSION
- AUTHOR, COURSE information

### Bangla Character Sets
- BANGLA_VOWELS (11 vowels)
- BANGLA_CONSONANTS (39+ consonants)
- BANGLA_DIACRITICS (10 diacritics)

### Error Type Definitions
- ERROR_TYPES dictionary (5 types)
- ERROR_DISTRIBUTION weights
- PHONETIC_MAP (similar sounding chars)
- VISUAL_MAP (similar looking chars)

### System Paths
- Paths to all data and output folders
- Resources and utilities locations

### Training Configuration
- Batch size, learning rate, epochs
- Max sequence length, beam size
- Random seed

### Dataset Proportions
- Train: 70%, Validation: 10%, Test: 20%

---

## 📝 Next Steps: Phase 1

After Phase 0 setup is complete, Phase 1 will implement:

1. **Corpus Collection**
   - Download Bangla text from Wikipedia, news, etc.
   - Collect 50,000-100,000 clean sentences

2. **Text Preprocessing**
   - Unicode normalization
   - HTML removal, character cleaning
   - Sentence and word tokenization
   - Duplicate removal

3. **Data Splitting**
   - Train/Validation/Test split (70/10/20)
   - Language model training on clean corpus

### Phase 1 Deliverables:
- Clean corpus (~50K-100K sentences)
- Train/val/test splits
- N-gram language model
- Preprocessing statistics

---

## ✅ Verification Checklist

Phase 0 Completion:
- ✓ Folder structure created
- ✓ All utility modules implemented
- ✓ Configuration file with constants
- ✓ Requirements.txt with all dependencies
- ✓ Setup scripts for Windows and Unix
- ✓ README with documentation
- ✓ Project structure diagram
- ✓ Placeholder files for all phases

System Ready For:
- ✓ Python environment setup
- ✓ Dependency installation
- ✓ Running Phase 1: Data Preprocessing

---

## 🔍 Project Statistics

### Files Created: 20+
### Folders Created: 18
### Total Project Size: Minimal (~500KB with code, grows with data)
### Python Modules: 4 (bangla_utils, metrics, io_utils, visualization)
### Setup Scripts: 2 (Windows, Unix)

---

## 📞 Troubleshooting Phase 0

### Issue: Setup script won't run on Windows
**Solution**: 
```bash
# Run PowerShell as admin, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
setup_environment.bat
```

### Issue: Permission denied on setup_environment.sh
**Solution**:
```bash
chmod +x setup_environment.sh
./setup_environment.sh
```

### Issue: Python not found
**Solution**: Install Python 3.8+ from https://www.python.org/

### Issue: Virtual environment not activating
**Solution**: Check Python installation and try manual setup:
```bash
python -m venv venv
```

---

## 📚 Documentation Structure

- `README.md` - Main project documentation
- `config.py` - Configuration reference
- `utils/` - Docstrings for utility functions
- Phase-specific README files (to be added)

---

## 🎯 Project Goals Recap

### Main Objective
Compare two approaches to Bangla spelling error correction:
1. Classical Noisy-Channel (statistical, lightweight)
2. Modern BanglaT5 Transformer (neural, powerful)

### Success Criteria
- ✓ Project structure organized
- ✓ All dependencies configured
- ✓ Utilities ready for use
- ⏳ Phase 1: Corpus preprocessing
- ⏳ Phase 2: Synthetic error generation
- ⏳ Phase 3: Noisy-Channel model
- ⏳ Phase 4: BanglaT5 fine-tuning
- ⏳ Phase 5: Comparative evaluation

---

## 📄 File Checklist for Phase 0

```
Phase 0: Project Initialization
├── ✓ requirements.txt
├── ✓ config.py
├── ✓ README.md
├── ✓ setup_environment.sh
├── ✓ setup_environment.bat
├── ✓ PHASE_0_SUMMARY.md (this file)
│
├── Folder Structure:
├── ✓ 1_Data_Preprocessing/
├── ✓ 2_Error_Generation/
├── ✓ 3_Noisy_Channel_Model/
├── ✓ 4_BanglaT5_Model/
├── ✓ 5_Evaluation/
├── ✓ resources/
├── ✓ utils/
│
├── Utility Modules:
├── ✓ utils/bangla_utils.py
├── ✓ utils/metrics.py
├── ✓ utils/io_utils.py
├── ✓ utils/visualization.py
│
└── Phase Placeholders:
    ├── ✓ 1_Data_Preprocessing/__init__.py
    ├── ✓ 2_Error_Generation/__init__.py
    ├── ✓ 3_Noisy_Channel_Model/__init__.py
    ├── ✓ 4_BanglaT5_Model/__init__.py
    └── ✓ 5_Evaluation/__init__.py
```

---

## 🎉 Phase 0 Status

**COMPLETE ✓**

The project structure for বানানরীতি (Bananriti) has been successfully initialized!

All folders, utilities, and configuration files are in place.

**Ready to proceed to Phase 1: Data Preprocessing and Corpus Preparation**

---

**Project**: বানানরীতি (Bananriti) - Bangla Spelling Error Correction
**Status**: Phase 0 Complete ✓
**Next**: Phase 1 - Data Preprocessing
**Date**: September 17, 2026
