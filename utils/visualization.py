"""
Visualization Utilities
Functions for creating charts and graphs
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List


def plot_confusion_matrix(cm: np.ndarray, labels: List[str],
                         title: str = 'Confusion Matrix',
                         save_path: str = None):
    """
    Plot confusion matrix

    Args:
        cm: Confusion matrix
        labels: Class labels
        title: Plot title
        save_path: Path to save figure
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

    plt.close()


def plot_metrics_comparison(metrics_dict: Dict[str, Dict[str, float]],
                           title: str = 'Model Comparison',
                           save_path: str = None):
    """
    Plot bar chart comparing metrics across models

    Args:
        metrics_dict: Dictionary of {model_name: {metric: value}}
        title: Plot title
        save_path: Path to save figure
    """
    models = list(metrics_dict.keys())
    metrics = list(metrics_dict[models[0]].keys())

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, model in enumerate(models):
        values = [metrics_dict[model][m] for m in metrics]
        ax.bar(x + i * width, values, width, label=model)

    ax.set_ylabel('Score (%)')
    ax.set_title(title)
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(metrics, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

    plt.close()


def plot_error_distribution(error_counts: Dict[str, int],
                           title: str = 'Error Type Distribution',
                           save_path: str = None):
    """
    Plot pie chart of error type distribution

    Args:
        error_counts: Dictionary of {error_type: count}
        title: Plot title
        save_path: Path to save figure
    """
    labels = list(error_counts.keys())
    sizes = list(error_counts.values())

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title(title)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

    plt.close()


def plot_training_curves(train_losses: List[float],
                         val_losses: List[float] = None,
                         title: str = 'Training Curves',
                         save_path: str = None):
    """
    Plot training loss curves

    Args:
        train_losses: Training losses per epoch
        val_losses: Validation losses per epoch (optional)
        title: Plot title
        save_path: Path to save figure
    """
    epochs = range(1, len(train_losses) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, train_losses, 'b-', label='Training Loss', linewidth=2)

    if val_losses:
        plt.plot(epochs, val_losses, 'r-', label='Validation Loss', linewidth=2)

    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

    plt.close()


# Placeholder for future implementations
def __init__():
    pass
