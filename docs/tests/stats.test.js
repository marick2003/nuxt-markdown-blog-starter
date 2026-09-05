import test from "node:test";
import assert from "node:assert/strict";
import { buildStats, segmentRallies } from "../js/pipeline/stats.js";

test("segmentRallies splits on long gap", () => {
  assert.deepEqual(segmentRallies([0.0, 0.5, 1.0, 6.0, 6.5], 4.0), [0, 0, 0, 1, 1]);
});

test("segmentRallies empty", () => {
  assert.deepEqual(segmentRallies([], 4.0), []);
});

test("buildStats counts and marks first hit of each rally", () => {
  const hits = [
    { t: 0.0, frameIndex: 0, side: "RIGHT", speed: 2.0 },
    { t: 0.5, frameIndex: 1, side: "LEFT", speed: 2.0 },
    { t: 6.0, frameIndex: 2, side: "RIGHT", speed: 2.0 },
  ];
  const seenFirstFlags = [];
  const classifyFn = (hit, isFirst) => {
    seenFirstFlags.push(isFirst);
    return "forehand";
  };

  const stats = buildStats(hits, classifyFn, 4.0);

  assert.equal(stats.rallyCount, 2);
  assert.deepEqual(stats.shotCounts, { forehand: 3 });
  assert.deepEqual(seenFirstFlags, [true, false, true]);
  assert.deepEqual(
    stats.shots.map((s) => s.rallyIndex),
    [0, 0, 1]
  );
});
