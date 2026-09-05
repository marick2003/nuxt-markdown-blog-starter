"""Video frame extraction using OpenCV."""
from __future__ import annotations

from typing import Iterator, Optional, Tuple

import cv2
import numpy as np


def iter_frames(video_path: str, sample_fps: Optional[float] = None) -> Iterator[Tuple[float, np.ndarray]]:
    """Yield (timestamp_seconds, bgr_frame) pairs from a video file.

    If `sample_fps` is given, frames are subsampled to approximately that
    rate instead of decoding every frame - pose estimation at native
    30/60fps is usually unnecessary and costly.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"could not open video: {video_path}")

    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, round(native_fps / sample_fps)) if sample_fps else 1

    frame_idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % step == 0:
                yield frame_idx / native_fps, frame
            frame_idx += 1
    finally:
        cap.release()
