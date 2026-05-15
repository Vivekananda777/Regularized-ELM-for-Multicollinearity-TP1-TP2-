import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import json
import os

def load_dataset(file_path, file_format):
    """Load dataset based on format."""
    if file_format == 'csv':
        return pd.read_csv(file_path)
    elif file_format in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    elif file_format == 'json':
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported format: {file_format}")

def preprocess_dataset(df, target_column=''):
    """Full preprocessing pipeline."""
    transformations = {}
    original_shape = df.shape

    # Handle missing values
    missing_before = df.isnull().sum().sum()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            transformations[col] = f'filled missing with median ({median_val:.2f})'

    for col in cat_cols:
        if df[col].isnull().any():
            mode_val = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
            df[col].fillna(mode_val, inplace=True)
            transformations[col] = f'filled missing with mode ({mode_val})'

    missing_after = df.isnull().sum().sum()
    missing_handled = int(missing_before - missing_after)

    # Encode categorical columns (exclude target)
    encoded_cols = []
    le = LabelEncoder()
    for col in cat_cols:
        if col != target_column:
            try:
                df[col] = le.fit_transform(df[col].astype(str))
                encoded_cols.append(col)
                if col not in transformations:
                    transformations[col] = 'label encoded'
                else:
                    transformations[col] += ', label encoded'
            except Exception:
                pass

    # Normalize numeric columns (exclude target)
    normalized_cols = []
    scaler = StandardScaler()
    cols_to_normalize = [c for c in numeric_cols if c != target_column]
    if cols_to_normalize:
        df[cols_to_normalize] = scaler.fit_transform(df[cols_to_normalize])
        normalized_cols = cols_to_normalize
        for col in cols_to_normalize:
            if col not in transformations:
                transformations[col] = 'standardized'
            else:
                transformations[col] += ', standardized'

    return df, {
        'missing_handled': missing_handled,
        'encoded_cols': encoded_cols,
        'normalized_cols': normalized_cols,
        'transformations': transformations,
        'original_rows': original_shape[0],
        'original_cols': original_shape[1],
        'feature_names': list(df.columns),
    }