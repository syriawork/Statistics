from __future__ import annotations

from typing import Dict, Sequence

import numpy as np


def estimate_shelf_life(times: Sequence[float], values: Sequence[float]) -> Dict[str, float]:
    if len(times) != len(values) or len(times) < 2:
        raise ValueError('Times and values must have the same length and at least two points.')
    x = np.asarray(times, dtype=float)
    y = np.asarray(values, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    return {
        'trend_slope': float(slope),
        'intercept': float(intercept),
        'correlation_coefficient': float(r),
        'r_squared': float(r ** 2),
        'degradation_rate': float(-slope),
        'shelf_life': float(-intercept / slope) if slope != 0 else float('nan'),
    }
