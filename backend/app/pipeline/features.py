"""Per-frame kinematic features derived from pose landmarks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from . import config

# (x, y, visibility) in MediaPipe's normalized image coordinates: x/y in
# [0, 1] relative to frame width/height, y increasing downward.
Landmark = Tuple[float, float, float]
Frame = Dict[str, Landmark]

REQUIRED_LANDMARKS = (
    "LEFT_SHOULDER",
    "RIGHT_SHOULDER",
    "LEFT_ELBOW",
    "RIGHT_ELBOW",
    "LEFT_WRIST",
    "RIGHT_WRIST",
    "LEFT_HIP",
    "RIGHT_HIP",
)


@dataclass
class FrameFeatures:
    t: float
    left_wrist_speed: float
    right_wrist_speed: float

    @property
    def dominant_side(self) -> str:
        return "RIGHT" if self.right_wrist_speed >= self.left_wrist_speed else "LEFT"

    @property
    def dominant_speed(self) -> float:
        return max(self.left_wrist_speed, self.right_wrist_speed)


def has_required_landmarks(frame: Frame, min_visibility: float = config.MIN_LANDMARK_VISIBILITY) -> bool:
    return all(
        name in frame and frame[name][2] >= min_visibility for name in REQUIRED_LANDMARKS
    )


def compute_frame_features(
    frames: List[Optional[Frame]], timestamps: List[float]
) -> List[Optional[FrameFeatures]]:
    """Compute wrist speed (normalized units / second) via finite differences.

    `frames[i]` is `None` where pose detection failed or no player was
    found in that frame.
    """
    if len(frames) != len(timestamps):
        raise ValueError("frames and timestamps must be the same length")

    features: List[Optional[FrameFeatures]] = [None] * len(frames)
    for i in range(1, len(frames)):
        prev, cur = frames[i - 1], frames[i]
        dt = timestamps[i] - timestamps[i - 1]
        if prev is None or cur is None or dt <= 0:
            continue
        if not (has_required_landmarks(prev) and has_required_landmarks(cur)):
            continue

        features[i] = FrameFeatures(
            t=timestamps[i],
            left_wrist_speed=_speed(prev["LEFT_WRIST"], cur["LEFT_WRIST"], dt),
            right_wrist_speed=_speed(prev["RIGHT_WRIST"], cur["RIGHT_WRIST"], dt),
        )
    return features


def _speed(a: Landmark, b: Landmark, dt: float) -> float:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return (dx * dx + dy * dy) ** 0.5 / dt
