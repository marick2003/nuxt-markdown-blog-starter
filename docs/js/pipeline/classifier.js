// Heuristic shot classification from pose at the moment of a hit.
// Mirrors backend/app/pipeline/classifier.py.
//
// This is a rule-based v1 classifier, not a trained model - there is no
// labeled squash footage available yet to train one. It distinguishes
// forehand/backhand by whether the hitting wrist has crossed the body's
// horizontal midline, and flags a rally's opening hit as a serve when
// contact happens above shoulder height. See the project README for
// accuracy caveats.

export const SHOT_FOREHAND = "forehand";
export const SHOT_BACKHAND = "backhand";
export const SHOT_SERVE = "serve";
export const SHOT_UNKNOWN = "unknown";

// Normalized-coordinate slack (image is [0, 1]) before a wrist counts as
// having crossed the torso midline, or a contact point counts as "above
// the shoulder". Both need tuning against real footage.
const CROSS_BODY_MARGIN = 0.03;
const SERVE_HEIGHT_MARGIN = 0.05;

/**
 * Classify a single hit given the pose at that frame.
 * `side` is "LEFT" or "RIGHT": the wrist that triggered the hit.
 */
export function classifyShot(frame, side, isFirstHitOfRally) {
  const shoulder = frame[`${side}_SHOULDER`];
  const wrist = frame[`${side}_WRIST`];
  const hipL = frame.LEFT_HIP;
  const hipR = frame.RIGHT_HIP;

  if (!shoulder || !wrist || !hipL || !hipR) return SHOT_UNKNOWN;

  // y grows downward, so a smaller y means a higher point on screen.
  if (isFirstHitOfRally && wrist[1] < shoulder[1] - SERVE_HEIGHT_MARGIN) {
    return SHOT_SERVE;
  }

  const torsoMidX = (hipL[0] + hipR[0]) / 2;
  const crossedMidline =
    (side === "RIGHT" && wrist[0] < torsoMidX - CROSS_BODY_MARGIN) ||
    (side === "LEFT" && wrist[0] > torsoMidX + CROSS_BODY_MARGIN);

  return crossedMidline ? SHOT_BACKHAND : SHOT_FOREHAND;
}
