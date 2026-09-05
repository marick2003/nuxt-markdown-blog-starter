"""Aggregate hit events into rallies and shot-type statistics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from .hit_detection import HitEvent

ClassifyFn = Callable[[HitEvent, bool], str]


@dataclass
class Shot:
    t: float
    side: str
    shot_type: str
    rally_index: int


@dataclass
class AnalysisStats:
    shots: List[Shot]
    rally_count: int
    shot_counts: Dict[str, int]


def segment_rallies(hit_times: List[float], rally_gap_seconds: float) -> List[int]:
    """Assign each hit a rally index.

    A gap longer than `rally_gap_seconds` between consecutive hits starts a
    new rally (the ball went out of play / point ended).
    """
    if not hit_times:
        return []
    rally_indices = [0]
    for prev_t, t in zip(hit_times, hit_times[1:]):
        rally_indices.append(rally_indices[-1] + (1 if t - prev_t > rally_gap_seconds else 0))
    return rally_indices


def build_stats(hits: List[HitEvent], classify_fn: ClassifyFn, rally_gap_seconds: float) -> AnalysisStats:
    """Build shot-level stats from hit events.

    `classify_fn(hit, is_first_hit_of_rally)` is injected so this module
    stays independent of pose data - it only knows about hit timing.
    """
    rally_indices = segment_rallies([h.t for h in hits], rally_gap_seconds)
    shots: List[Shot] = []
    shot_counts: Dict[str, int] = {}

    for i, (hit, rally_idx) in enumerate(zip(hits, rally_indices)):
        is_first = i == 0 or rally_indices[i - 1] != rally_idx
        shot_type = classify_fn(hit, is_first)
        shots.append(Shot(t=hit.t, side=hit.side, shot_type=shot_type, rally_index=rally_idx))
        shot_counts[shot_type] = shot_counts.get(shot_type, 0) + 1

    rally_count = (rally_indices[-1] + 1) if rally_indices else 0
    return AnalysisStats(shots=shots, rally_count=rally_count, shot_counts=shot_counts)
