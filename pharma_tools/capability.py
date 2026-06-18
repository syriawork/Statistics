from __future__ import annotations

from typing import Dict, Sequence

import numpy as np


def _normalize_data(data: Sequence[float]) -> np.ndarray:
    arr = np.asarray(data, dtype=float)
    if arr.size < 2:
        raise ValueError('Data must contain at least two numeric values.')
    return arr


def calculate_cp(data: Sequence[float], usl: float, lsl: float) -> float:
    arr = _normalize_data(data)
    sigma = float(np.std(arr, ddof=1))
    if sigma == 0:
        return float('nan')
    return float((usl - lsl) / (6.0 * sigma))


def calculate_cpk(data: Sequence[float], usl: float, lsl: float) -> float:
    arr = _normalize_data(data)
    mean = float(np.mean(arr))
    sigma = float(np.std(arr, ddof=1))
    if sigma == 0:
        return float('nan')
    cpu = (usl - mean) / (3.0 * sigma)
    cpl = (mean - lsl) / (3.0 * sigma)
    return float(min(cpu, cpl))


def calculate_ppk(data: Sequence[float], usl: float, lsl: float) -> float:
    arr = _normalize_data(data)
    mean = float(np.mean(arr))
    sigma = float(np.std(arr, ddof=0))
    if sigma == 0:
        return float('nan')
    cpu = (usl - mean) / (3.0 * sigma)
    cpl = (mean - lsl) / (3.0 * sigma)
    return float(min(cpu, cpl))


def calculate_process_capability(data: Sequence[float], usl: float, lsl: float) -> Dict[str, float]:
    arr = _normalize_data(data)
    return {
        'cp': calculate_cp(arr, usl, lsl),
        'cpk': calculate_cpk(arr, usl, lsl),
        'ppk': calculate_ppk(arr, usl, lsl),
        'mean': float(np.mean(arr)),
        'std_sample': float(np.std(arr, ddof=1)),
        'std_population': float(np.std(arr, ddof=0)),
    }
