// Tunable thresholds for the analysis pipeline. Mirrors
// backend/app/pipeline/config.py - keep the two in sync if you tune one.
//
// These are reasonable starting points, not values calibrated against real
// squash footage. In particular WRIST_SPEED_THRESHOLD is sensitive to
// camera distance/resolution and should be tuned per venue/camera setup.

// Frames-per-second to sample the source video at.
export const SAMPLE_FPS = 15.0;

// Minimum wrist speed (normalized image units / second) to consider a
// frame a candidate hit.
export const WRIST_SPEED_THRESHOLD = 1.2;

// Minimum time between two detected hits; prevents one swing's speed curve
// from being counted as multiple hits.
export const REFRACTORY_SECONDS = 0.3;

// A gap longer than this between consecutive hits is treated as the end of
// one rally and the start of the next.
export const RALLY_GAP_SECONDS = 4.0;

// Landmarks below this visibility score are treated as untracked.
export const MIN_LANDMARK_VISIBILITY = 0.4;

// MediaPipe Pose Landmarker model bundle, loaded directly in the browser.
export const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task";

export const TASKS_VISION_VERSION = "0.10.14";
export const TASKS_VISION_CDN = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${TASKS_VISION_VERSION}`;
