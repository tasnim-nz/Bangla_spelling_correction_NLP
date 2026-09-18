"""
Project Configuration and Constants
"""

# Project Metadata
PROJECT_NAME = "বানানরীতি (Bananriti)"
PROJECT_DESCRIPTION = "Bangla Spelling Error Correction System"
VERSION = "1.0.0"
AUTHOR = "NLP Lab Student"
COURSE = "CSE 4122 - Natural Language Processing Laboratory"

# Bangla Character Sets
BANGLA_VOWELS = ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ']
BANGLA_CONSONANTS = [
    'ক', 'খ', 'গ', 'ঘ', 'ঙ',
    'চ', 'ছ', 'জ', 'ঝ', 'ঞ',
    'ট', 'ঠ', 'ড', 'ঢ', 'ণ',
    'ত', 'থ', 'দ', 'ধ', 'ন',
    'প', 'ফ', 'ব', 'ভ', 'ম',
    'য', 'র', 'ল', 'শ', 'ষ', 'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ'
]

BANGLA_DIACRITICS = ['া', 'ি', 'ী', 'ু', 'ূ', 'ৃ', 'ে', 'ৈ', 'ো', 'ৌ']

# Error Types
ERROR_TYPES = {
    'phonetic': 'Phonetic errors (similar sounds)',
    'visual': 'Visual errors (similar appearance)',
    'typographical': 'Typographical errors (insertion, deletion, substitution, transposition)',
    'split_word': 'Split-word errors (incorrect spacing)',
    'run_on': 'Run-on errors (joined words)'
}

# Error Distribution (proportions)
ERROR_DISTRIBUTION = {
    'typographical': 0.35,
    'phonetic': 0.30,
    'visual': 0.20,
    'split_word': 0.10,
    'run_on': 0.05
}

# Phonetic Similarity Map (similar sounding Bangla characters)
PHONETIC_MAP = {
    'ড': ['ঢ'],
    'ঢ': ['ড'],
    'ত': ['ট'],
    'ট': ['ত'],
    'স': ['ষ'],
    'ষ': ['স'],
}

# Visual Similarity Map (visually similar Bangla characters)
VISUAL_MAP = {
    'ব': ['য়', 'ঠ'],
    'য়': ['ব'],
    'ঠ': ['ব'],
    'ক': ['খ'],
    'খ': ['ক'],
}

# Model Paths
PATHS = {
    'corpus': '1_Data_Preprocessing/outputs/',
    'errors': '2_Error_Generation/outputs/',
    'nc_model': '3_Noisy_Channel_Model/outputs/',
    'bangla_t5': '4_BanglaT5_Model/outputs/',
    'evaluation': '5_Evaluation/outputs/',
    'resources': 'resources/',
    'utils': 'utils/'
}

# Training Configuration
TRAINING_CONFIG = {
    'batch_size': 32,
    'learning_rate': 5e-5,
    'epochs': 3,
    'max_length': 256,
    'beam_size': 4,
    'seed': 42,
}

# Dataset Sizes
DATASET_SIZES = {
    'train': 0.70,
    'validation': 0.10,
    'test': 0.20
}
