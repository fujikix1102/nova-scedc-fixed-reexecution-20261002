"""Conservative three-component seismic onset picker.

The picker is exploratory: it returns candidates and diagnostics, never a
formal timing guarantee. Inputs must be equally sampled and time aligned.
"""
import numpy as np


def polarization_linearity(components: np.ndarray) -> float:
    x = np.asarray(components, dtype=float)
    if x.ndim != 2 or x.shape[0] != 3 or x.shape[1] < 3:
        raise ValueError("components must have shape (3, n>=3)")
    if not np.isfinite(x).all():
        return float("nan")
    x = x - x.mean(axis=1, keepdims=True)
    eig = np.linalg.eigvalsh(np.cov(x))
    total = float(eig.sum())
    return float(eig[-1] / total) if total > 0 else 0.0


def pick_three_component(sta_lta: np.ndarray, components: np.ndarray,
                         sample_rate_hz: float, threshold: float = 3.0,
                         window_seconds: float = 0.5) -> dict:
    """Return the candidate maximizing STA/LTA-weighted linearity."""
    cft = np.asarray(sta_lta, dtype=float)
    data = np.asarray(components, dtype=float)
    if data.ndim != 2 or data.shape[0] != 3 or data.shape[1] != cft.size:
        raise ValueError("components and STA/LTA length mismatch")
    if sample_rate_hz <= 0 or not np.isfinite(cft).all():
        raise ValueError("invalid sampling rate or STA/LTA")
    half = max(2, int(round(window_seconds * sample_rate_hz)))
    candidates = []
    for i in np.flatnonzero(cft >= threshold):
        lo, hi = max(0, i - half), min(cft.size, i + half)
        lin = polarization_linearity(data[:, lo:hi])
        if np.isfinite(lin):
            candidates.append({"sample": int(i), "time_s": float(i / sample_rate_hz),
                               "sta_lta": float(cft[i]), "linearity": lin,
                               "score": float(cft[i] * lin)})
    candidates.sort(key=lambda x: (-x["score"], x["sample"]))
    return {"status": "CANDIDATE" if candidates else "NO_CANDIDATE",
            "selected": candidates[0] if candidates else None,
            "candidates": candidates,
            "formal_pass": False,
            "claim_boundary": "Exploratory onset candidate only."}
