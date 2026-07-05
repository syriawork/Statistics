from __future__ import annotations

from typing import Dict, Sequence

import numpy as np


def calculate_f1_f2(reference: Sequence[float], test: Sequence[float]) -> Dict[str, float]:
    """Calculate similarity and difference factors for dissolution profiles."""
    ref = np.asarray(reference, dtype=float)
    tst = np.asarray(test, dtype=float)
    if ref.shape != tst.shape or ref.size == 0:
        raise ValueError('Reference and test profiles must have the same non-empty length.')
    f1 = float(np.sum(np.abs(ref - tst)) / np.sum(np.abs(ref)) * 100)
    f2 = float(50 * np.log10((1 + 0.05 * np.sum((ref - tst) ** 2)) ** -0.5 * 100))
    interpretation = 'Similar' if 50 <= f2 <= 100 else 'Not similar'
    return {
        'f1': f1,
        'f2': f2,
        'interpretation': interpretation,
    }
