// End-to-end squash video analysis pipeline (pose-independent part).
// Mirrors backend/app/pipeline/__init__.py:analyze_frames.
//
// Kept separate from pose/video capture so it can be unit-tested with
// synthetic landmark data under Node, without a browser or MediaPipe.

import * as config from "./config.js";
import { computeFrameFeatures } from "./features.js";
import { detectHits } from "./hit_detection.js";
import { classifyShot } from "./classifier.js";
import { buildStats } from "./stats.js";

export function analyzeFrames(frames, timestamps) {
  const features = computeFrameFeatures(frames, timestamps, config.MIN_LANDMARK_VISIBILITY);
  const hits = detectHits(features, config.WRIST_SPEED_THRESHOLD, config.REFRACTORY_SECONDS);

  const classifyFn = (hit, isFirst) => {
    const frame = frames[hit.frameIndex];
    if (!frame) return "unknown";
    return classifyShot(frame, hit.side, isFirst);
  };

  const stats = buildStats(hits, classifyFn, config.RALLY_GAP_SECONDS);
  const duration = timestamps.length ? timestamps[timestamps.length - 1] : 0;
  return { stats, duration };
}

export { config };
