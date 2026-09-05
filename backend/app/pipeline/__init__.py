"""End-to-end squash video analysis pipeline."""
from __future__ import annotations

from typing import List, Optional, Tuple

from . import config
from .classifier import classify_shot
from .features import Frame, compute_frame_features
from .hit_detection import detect_hits
from .stats import AnalysisStats, build_stats


def analyze_video(video_path: str) -> Tuple[AnalysisStats, float]:
    """Run the full pipeline (decode -> pose -> hits -> classify -> stats) on a video file."""
    from .pose import PoseExtractor
    from .video_io import iter_frames

    frames: List[Optional[Frame]] = []
    timestamps: List[float] = []

    with PoseExtractor() as pose:
        for t, bgr in iter_frames(video_path, sample_fps=config.SAMPLE_FPS):
            timestamps.append(t)
            frames.append(pose.extract(bgr, timestamp_ms=int(t * 1000)))

    return analyze_frames(frames, timestamps)


def analyze_frames(
    frames: List[Optional[Frame]], timestamps: List[float]
) -> Tuple[AnalysisStats, float]:
    """Runs the pose-independent part of the pipeline.

    Kept separate from `analyze_video` so it can be unit-tested with
    synthetic landmark data, without needing OpenCV/MediaPipe or a real
    video file.
    """
    features = compute_frame_features(frames, timestamps)
    hits = detect_hits(features, config.WRIST_SPEED_THRESHOLD, config.REFRACTORY_SECONDS)

    def classify_fn(hit, is_first_hit_of_rally: bool) -> str:
        frame = frames[hit.frame_index]
        if frame is None:
            return "unknown"
        return classify_shot(frame, hit.side, is_first_hit_of_rally)

    stats = build_stats(hits, classify_fn, config.RALLY_GAP_SECONDS)
    duration = timestamps[-1] if timestamps else 0.0
    return stats, duration
