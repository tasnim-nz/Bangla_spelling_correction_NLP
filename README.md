# বানানরীতি (Bananriti)

**Bangla Spelling Error Correction System**

A comparative study of classical Noisy-Channel Model vs. modern Transformer-based (BanglaT5) approaches for Bangla spelling error correction.

## 📋 Project Overview

This project implements and compares two distinct approaches for automatic Bangla spelling error correction:

1. **Classical Noisy-Channel Model** - Statistical, interpretable, lightweight
2. **BanglaT5 Transformer Model** - Neural, context-aware, data-hungry

### Course Information
- **Course**: Natural Language Processing Laboratory (CSE 4122)
- **Project Date**: September 2026
- **Type**: Comparative Implementation Study

## 🎯 Objectives

- Develop synthetic Bangla spelling error generator
- Implement classical noisy-channel spelling corrector
- Fine-tune BanglaT5 for spelling correction
- Systematically compare both approaches
- Understand trade-offs: accuracy vs. efficiency

## 📂 Project Structure

```
Bananriti/
├── 1_Data_Preprocessing/          # Corpus collection & cleaning
│   ├── outputs/                   # Clean corpus, train/val/test splits
│   ├── download_corpus.py
│   ├── preprocess.py
│   └── split_corpus.py
│
├── 2_Error_Generation/            # Synthetic error creation
│   ├── outputs/                   # Erroneous text, parallel corpus
│   ├── error_generator.py
│   └── error_patterns.py
│
├── 3_Noisy_Channel_Model/        # Classical approach
│   ├── outputs/                   # Saved models, predictions
│   ├── build_nc_model.py
│   ├── ngram_lm.py
│   ├── error_model.py
│   ├── candidate_generator.py
│   └── inference_nc.py
│
├── 4_BanglaT5_Model/             # Transformer approach
│   ├── configs/                   # Training configurations
│   ├── outputs/                   # Fine-tuned model, logs
│   ├── prepare_data.py
│   ├── fine_tune.py
│   └── inference_t5.py
│
├── 5_Evaluation/                  # Comparison & analysis
│   ├── outputs/                   # Results, visualizations
│   ├── evaluate.py
│   ├── compare_models.py
│   ├── error_analysis.py
│   └── visualize_results.py
│
├── resources/                     # Dictionaries, mappings
│   ├── keyboard_maps/            # Avro, Bijoy layouts
│   ├── bangla_dictionary.txt
│   ├── phonetic_map.json
│   └── visual_map.json
│
├── utils/                         # Shared utilities
│   ├── bangla_utils.py
│   ├── metrics.py
│   ├── io_utils.py
│   └── visualization.py
│
├── requirements.txt               # Python dependencies
├── setup_environment.bat          # Windows setup script
├── setup_environment.sh           # Unix setup script
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 8GB+ RAM (16GB+ recommended for BanglaT5)
- GPU with CUDA (optional but recommended for BanglaT5)

### Installation

**On Windows:**
```bash
setup_environment.bat
```

**On Mac/Linux:**
```bash
chmod +x setup_environment.sh
./setup_environment.sh
```

**Manual Setup:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

## 📊 Implementation Phases

### Phase 1: Data Preprocessing
```bash
cd 1_Data_Preprocessing
python download_corpus.py    # Download Bangla corpus
python preprocess.py          # Clean and normalize
python split_corpus.py        # Train/val/test split
```

### Phase 2: Error Generation
```bash
cd 2_Error_Generation
python error_generator.py     # Generate synthetic errors
```

### Phase 3: Noisy-Channel Model
```bash
cd 3_Noisy_Channel_Model
python build_nc_model.py      # Train classical model
python inference_nc.py        # Test predictions
```

### Phase 4: BanglaT5 Model
```bash
cd 4_BanglaT5_Model
python prepare_data.py        # Format for HuggingFace
python fine_tune.py           # Fine-tune BanglaT5
python inference_t5.py        # Test predictions
```

### Phase 5: Evaluation
```bash
cd 5_Evaluation
python evaluate.py            # Calculate metrics
python compare_models.py      # Comparative analysis
python visualize_results.py   # Generate charts
```

## 🔍 Bangla Error Types

The system handles five main error categories:

1. **Phonetic Errors** - Similar sounding characters (ড↔ঢ, ত↔ট)
2. **Visual Errors** - Visually similar characters (ব↔য়)
3. **Typographical Errors** - Insertion, deletion, substitution, transposition
4. **Split-Word Errors** - Incorrect word spacing
5. **Run-on Errors** - Multiple words joined together

## 📈 Expected Results

### Noisy-Channel Model
- Exact Match: 65-75%
- Character Error Rate: 3-8%
- Word-level F1: 70-80%
- Inference: <100ms per sentence (CPU)

### BanglaT5 Model
- Exact Match: 75-85%
- Character Error Rate: 2-6%
- Word-level F1: 78-88%
- Inference: 50-200ms per sentence (GPU)

## 🛠️ Technologies

- **PyTorch** - Deep learning framework
- **Transformers (Hugging Face)** - BanglaT5 model
- **NLTK** - Text processing utilities
- **NumPy/Pandas** - Data manipulation
- **Matplotlib/Seaborn** - Visualization

## 📚 References

1. Kernighan, M. D., Church, K. W., & Gale, W. A. (1990). A Spelling Correction Program Based on a Noisy Channel Model. COLING 1990.

2. Bhattacharjee, A., Hasan, T., Ahmad, W. U., & Shahriyar, R. (2023). BanglaNLG and BanglaT5. EACL 2023. arXiv:2205.11081

3. Bijoy, M. H., Hossain, N., Islam, S., & Shatabda, S. (2025). A Transformer-Based Spelling Error Correction Framework for Bangla. Computer Speech & Language, 89, 101703.

## 🤝 Contributing

This is an academic project for CSE 4122. For questions or suggestions, please refer to the course instructor.

## 📄 License

Academic use only. See course guidelines for usage terms.

## 🎓 Acknowledgments

- Course: Natural Language Processing Laboratory (CSE 4122)
- Pretrained models from Hugging Face
- Bangla NLP community resources

---

**Created**: September 2026  
**Status**: Phase 0 Complete - Project structure initialized  
**Next Step**: Phase 1 - Data Preprocessing
