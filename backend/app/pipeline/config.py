"""Tunable thresholds for the analysis pipeline.

These are reasonable starting points, not values calibrated against real
squash footage. In particular `WRIST_SPEED_THRESHOLD` is sensitive to
camera distance/resolution and should be tuned per venue/camera setup.
"""

# Frames-per-second to sample the source video at. Squash rallies are fast,
# but pose estimation at native 30/60fps is usually unnecessary and costly.
SAMPLE_FPS = 15.0

# Minimum wrist speed (normalized image units / second) to consider a frame
# a candidate hit. Normalized units means the landmark coordinates are in
# [0, 1] relative to frame width/height, as returned by MediaPipe.
WRIST_SPEED_THRESHOLD = 1.2

# Minimum time between two detected hits; prevents one swing's speed curve
# from being counted as multiple hits.
REFRACTORY_SECONDS = 0.3

# A gap longer than this between consecutive hits is treated as the end of
# one rally and the start of the next.
RALLY_GAP_SECONDS = 4.0

# Landmarks below this visibility score are treated as untracked.
MIN_LANDMARK_VISIBILITY = 0.4
