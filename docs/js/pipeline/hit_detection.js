// Detect hit events (racket-ball contact moments) from wrist-speed peaks.
// Mirrors backend/app/pipeline/hit_detection.py.

/**
 * Find wrist-speed local maxima above `speedThreshold`.
 *
 * A swing produces a smooth speed curve spanning several sampled frames;
 * picking local maxima and then merging any that fall within
 * `refractorySeconds` of each other collapses that curve down to one event
 * per actual swing.
 */
export function detectHits(features, speedThreshold, refractorySeconds, window = 2) {
  const candidates = [];
  for (let i = 0; i < features.length; i++) {
    const f = features[i];
    if (!f || f.dominantSpeed < speedThreshold) continue;
    if (isLocalPeak(features, i, window)) {
      candidates.push({ t: f.t, frameIndex: i, side: f.dominantSide, speed: f.dominantSpeed });
    }
  }

  if (candidates.length === 0) return [];

  const merged = [candidates[0]];
  for (let i = 1; i < candidates.length; i++) {
    const c = candidates[i];
    const last = merged[merged.length - 1];
    if (c.t - last.t < refractorySeconds) {
      if (c.speed > last.speed) merged[merged.length - 1] = c;
    } else {
      merged.push(c);
    }
  }
  return merged;
}

function isLocalPeak(features, i, window) {
  const target = features[i].dominantSpeed;
  const lo = Math.max(0, i - window);
  const hi = Math.min(features.length, i + window + 1);
  for (let j = lo; j < hi; j++) {
    const f = features[j];
    if (f && f.dominantSpeed > target) return false;
  }
  return true;
}
