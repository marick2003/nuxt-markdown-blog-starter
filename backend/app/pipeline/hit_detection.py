"""Detect hit events (racket-ball contact moments) from wrist-speed peaks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .features import FrameFeatures


@dataclass
class HitEvent:
    t: float
    frame_index: int
    side: str  # "LEFT" or "RIGHT" - which wrist triggered it
    speed: float


def detect_hits(
    features: List[Optional[FrameFeatures]],
    speed_threshold: float,
    refractory_seconds: float,
    window: int = 2,
) -> List[HitEvent]:
    """Find wrist-speed local maxima above `speed_threshold`.

    A swing produces a smooth speed curve spanning several sampled frames;
    picking local maxima and then merging any that fall within
    `refractory_seconds` of each other collapses that curve down to one
    event per actual swing.
    """
    candidates: List[HitEvent] = []
    for i, f in enumerate(features):
        if f is None or f.dominant_speed < speed_threshold:
            continue
        if _is_local_peak(features, i, window):
            candidates.append(HitEvent(t=f.t, frame_index=i, side=f.dominant_side, speed=f.dominant_speed))

    if not candidates:
        return []

    merged: List[HitEvent] = [candidates[0]]
    for c in candidates[1:]:
        if c.t - merged[-1].t < refractory_seconds:
            if c.speed > merged[-1].speed:
                merged[-1] = c
        else:
            merged.append(c)
    return merged


def _is_local_peak(features: List[Optional[FrameFeatures]], i: int, window: int) -> bool:
    target = features[i].dominant_speed
    lo, hi = max(0, i - window), min(len(features), i + window + 1)
    for j in range(lo, hi):
        f = features[j]
        if f is not None and f.dominant_speed > target:
            return False
    return True
