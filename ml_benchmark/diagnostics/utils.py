import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor
import io
import os
import uuid

def compute_vif(df, target_column=''):
    """Compute VIF for all numeric features."""
    numeric_df = df.select_dtypes(include=[np.number])
    if target_column and target_column in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=[target_column])
    numeric_df = numeric_df.dropna()
    if numeric_df.shape[1] < 2:
        return {}
    vif_data = {}
    for i, col in enumerate(numeric_df.columns):
        try:
            vif = variance_inflation_factor(numeric_df.values, i)
            vif_data[col] = round(float(vif), 4) if np.isfinite(vif) else 999.0
        except Exception:
            vif_data[col] = None
    return vif_data

def compute_correlation_matrix(df, target_column=''):
    """Compute correlation matrix for numeric features."""
    numeric_df = df.select_dtypes(include=[np.number])
    if target_column and target_column in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=[target_column])
    corr = numeric_df.corr()
    return corr.round(4).to_dict()

def generate_heatmap(df, target_column='', save_path=None):
    """Generate seaborn heatmap and save as image."""
    numeric_df = df.select_dtypes(include=[np.number])
    if target_column and target_column in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=[target_column])

    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(max(8, len(corr.columns)), max(6, len(corr.columns) - 1)))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
                center=0, vmin=-1, vmax=1, ax=ax,
                linewidths=0.5, cbar_kws={'shrink': 0.8})
    ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path