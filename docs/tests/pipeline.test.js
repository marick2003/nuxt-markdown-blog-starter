import test from "node:test";
import assert from "node:assert/strict";
import { analyzeFrames } from "../js/pipeline/index.js";

function frame(rightWristX, rightWristY = 0.5) {
  return {
    RIGHT_SHOULDER: [0.6, 0.3, 0.9],
    LEFT_SHOULDER: [0.4, 0.3, 0.9],
    RIGHT_ELBOW: [0.65, 0.4, 0.9],
    LEFT_ELBOW: [0.35, 0.4, 0.9],
    RIGHT_WRIST: [rightWristX, rightWristY, 0.9],
    LEFT_WRIST: [0.3, 0.6, 0.9],
    LEFT_HIP: [0.45, 0.6, 0.9],
    RIGHT_HIP: [0.55, 0.6, 0.9],
  };
}

test("analyzeFrames end-to-end detects one forehand", () => {
  const xs = [0.6, 0.6, 0.6, 0.6, 0.9, 0.65, 0.6, 0.6];
  const frames = xs.map((x) => frame(x));
  const timestamps = xs.map((_, i) => i * 0.1);

  const { stats, duration } = analyzeFrames(frames, timestamps);

  assert.equal(stats.rallyCount, 1);
  assert.deepEqual(stats.shotCounts, { forehand: 1 });
  assert.equal(duration, timestamps[timestamps.length - 1]);
});

test("analyzeFrames two rallies with gap", () => {
  const xs = [0.6, 0.6, 0.9, 0.6, 0.6, 0.6, 0.6, 0.6, 0.9, 0.6];
  const frames = xs.map((x) => frame(x));
  const timestamps = [0.0, 0.1, 0.2, 0.3, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5];

  const { stats } = analyzeFrames(frames, timestamps);

  assert.equal(stats.rallyCount, 2);
  assert.equal(
    Object.values(stats.shotCounts).reduce((a, b) => a + b, 0),
    2
  );
});

test("analyzeFrames handles missing pose gracefully", () => {
  const frames = [null, null, null];
  const timestamps = [0.0, 0.1, 0.2];

  const { stats, duration } = analyzeFrames(frames, timestamps);

  assert.deepEqual(stats.shots, []);
  assert.equal(stats.rallyCount, 0);
  assert.equal(duration, 0.2);
});
