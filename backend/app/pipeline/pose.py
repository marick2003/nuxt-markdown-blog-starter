"""MediaPipe Pose (Tasks API) wrapper: extract named landmark coordinates per frame.

Kept isolated so the rest of the pipeline (features/hit_detection/
classifier/stats) never imports mediapipe or opencv directly, which keeps
their unit tests fast and dependency-free.

Uses MediaPipe's Tasks API (`PoseLandmarker`) rather than the older
`mediapipe.solutions` API - recent MediaPipe wheels no longer ship the
legacy `solutions` module, and Tasks is Google's current recommended API.
It needs a small model bundle (~6MB), which is downloaded on first use and
cached under `models/` (see `_ensure_model`).
"""
from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision

from .features import Frame

_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "pose_landmarker_lite.task"

# Subset of MediaPipe's 33 pose landmarks that the pipeline actually uses.
_LANDMARK_NAMES = {
    0: "NOSE",
    11: "LEFT_SHOULDER",
    12: "RIGHT_SHOULDER",
    13: "LEFT_ELBOW",
    14: "RIGHT_ELBOW",
    15: "LEFT_WRIST",
    16: "RIGHT_WRIST",
    23: "LEFT_HIP",
    24: "RIGHT_HIP",
}


def _ensure_model() -> Path:
    if not _MODEL_PATH.exists():
        _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
    return _MODEL_PATH


class PoseExtractor:
    def __init__(self, model_path: Optional[Path] = None, num_poses: int = 1):
        options = vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path or _ensure_model())),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=num_poses,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(options)

    def extract(self, bgr_frame, timestamp_ms: int) -> Optional[Frame]:
        """Run pose detection on one frame.

        `timestamp_ms` must be strictly increasing across calls on the same
        `PoseExtractor` (MediaPipe's VIDEO running mode requirement) - pass
        the frame's real timestamp in the source video, in milliseconds.
        """
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.pose_landmarks:
            return None

        landmarks = result.pose_landmarks[0]
        frame: Frame = {}
        for idx, name in _LANDMARK_NAMES.items():
            lm = landmarks[idx]
            frame[name] = (lm.x, lm.y, lm.visibility)
        return frame

    def close(self) -> None:
        self._landmarker.close()

    def __enter__(self) -> "PoseExtractor":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
