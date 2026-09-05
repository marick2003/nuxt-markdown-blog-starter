// Per-frame kinematic features derived from pose landmarks.
// Mirrors backend/app/pipeline/features.py.
//
// A "frame" is a plain object keyed by landmark name -> [x, y, visibility]
// in MediaPipe's normalized image coordinates: x/y in [0, 1] relative to
// frame width/height, y increasing downward. `null` means pose detection
// failed / no player was found in that frame.

export const REQUIRED_LANDMARKS = [
  "LEFT_SHOULDER",
  "RIGHT_SHOULDER",
  "LEFT_ELBOW",
  "RIGHT_ELBOW",
  "LEFT_WRIST",
  "RIGHT_WRIST",
  "LEFT_HIP",
  "RIGHT_HIP",
];

export function hasRequiredLandmarks(frame, minVisibility) {
  if (!frame) return false;
  return REQUIRED_LANDMARKS.every((name) => frame[name] && frame[name][2] >= minVisibility);
}

function makeFrameFeatures(t, leftWristSpeed, rightWristSpeed) {
  return {
    t,
    leftWristSpeed,
    rightWristSpeed,
    get dominantSide() {
      return this.rightWristSpeed >= this.leftWristSpeed ? "RIGHT" : "LEFT";
    },
    get dominantSpeed() {
      return Math.max(this.leftWristSpeed, this.rightWristSpeed);
    },
  };
}

function speed(a, b, dt) {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  return Math.sqrt(dx * dx + dy * dy) / dt;
}

/**
 * Compute wrist speed (normalized units / second) via finite differences.
 * `frames[i]` is `null` where pose detection failed or no player was found.
 */
export function computeFrameFeatures(frames, timestamps, minVisibility) {
  if (frames.length !== timestamps.length) {
    throw new Error("frames and timestamps must be the same length");
  }

  const features = new Array(frames.length).fill(null);
  for (let i = 1; i < frames.length; i++) {
    const prev = frames[i - 1];
    const cur = frames[i];
    const dt = timestamps[i] - timestamps[i - 1];
    if (!prev || !cur || dt <= 0) continue;
    if (!hasRequiredLandmarks(prev, minVisibility) || !hasRequiredLandmarks(cur, minVisibility)) continue;

    features[i] = makeFrameFeatures(
      timestamps[i],
      speed(prev.LEFT_WRIST, cur.LEFT_WRIST, dt),
      speed(prev.RIGHT_WRIST, cur.RIGHT_WRIST, dt)
    );
  }
  return features;
}
