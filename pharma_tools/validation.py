from __future__ import annotations

from typing import Dict, Sequence

import numpy as np


def generate_validation_summary(data: Sequence[float]) -> Dict[str, float]:
    arr = np.asarray(data, dtype=float)
    if arr.size == 0:
        raise ValueError('Validation data must contain at least one numeric value.')
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
    r2 = 1.0 if arr.size < 2 else float(np.corrcoef(arr, arr)[0, 1])
    return {
        'accuracy': mean,
        'precision': std,
        'repeatability': std,
        'intermediate_precision': std,
        'linearity': float(np.nan),
        'regression_equation': 'y = x',
        'correlation_coefficient': r2,
        'r_squared': r2 ** 2,
        'lod': float(np.nan),
        'loq': float(np.nan),
        'robustness': float(np.nan),
    }
