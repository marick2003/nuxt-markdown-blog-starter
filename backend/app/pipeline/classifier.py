"""Heuristic shot classification from pose at the moment of a hit.

This is a rule-based v1 classifier, not a trained model - there is no
labeled squash footage available yet to train one. It distinguishes
forehand/backhand by whether the hitting wrist has crossed the body's
horizontal midline, and flags a rally's opening hit as a serve when
contact happens above shoulder height. See the project README for
accuracy caveats and the plan to replace this with a learned classifier.
"""
from __future__ import annotations

from typing import Optional

from .features import Frame, Landmark

SHOT_FOREHAND = "forehand"
SHOT_BACKHAND = "backhand"
SHOT_SERVE = "serve"
SHOT_UNKNOWN = "unknown"

# Normalized-coordinate slack (image is [0, 1]) before a wrist counts as
# having crossed the torso midline, or a contact point counts as "above
# the shoulder". Both need tuning against real footage.
CROSS_BODY_MARGIN = 0.03
SERVE_HEIGHT_MARGIN = 0.05


def classify_shot(frame: Frame, side: str, is_first_hit_of_rally: bool) -> str:
    """Classify a single hit given the pose at that frame.

    `side` is "LEFT" or "RIGHT": the wrist that triggered the hit.
    """
    shoulder: Optional[Landmark] = frame.get(f"{side}_SHOULDER")
    wrist: Optional[Landmark] = frame.get(f"{side}_WRIST")
    hip_l: Optional[Landmark] = frame.get("LEFT_HIP")
    hip_r: Optional[Landmark] = frame.get("RIGHT_HIP")

    if not all([shoulder, wrist, hip_l, hip_r]):
        return SHOT_UNKNOWN

    # y grows downward, so a smaller y means a higher point on screen.
    if is_first_hit_of_rally and wrist[1] < shoulder[1] - SERVE_HEIGHT_MARGIN:
        return SHOT_SERVE

    torso_mid_x = (hip_l[0] + hip_r[0]) / 2
    crossed_midline = (side == "RIGHT" and wrist[0] < torso_mid_x - CROSS_BODY_MARGIN) or (
        side == "LEFT" and wrist[0] > torso_mid_x + CROSS_BODY_MARGIN
    )
    return SHOT_BACKHAND if crossed_midline else SHOT_FOREHAND
