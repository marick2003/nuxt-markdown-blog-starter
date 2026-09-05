import test from "node:test";
import assert from "node:assert/strict";
import { detectHits } from "../js/pipeline/hit_detection.js";

function features(speeds) {
  return speeds.map((s, i) => ({
    t: i * 0.1,
    leftWristSpeed: 0,
    rightWristSpeed: s,
    get dominantSide() {
      return this.rightWristSpeed >= this.leftWristSpeed ? "RIGHT" : "LEFT";
    },
    get dominantSpeed() {
      return Math.max(this.leftWristSpeed, this.rightWristSpeed);
    },
  }));
}

test("detects single clear peak", () => {
  const hits = detectHits(features([0, 0.2, 0.5, 2.0, 0.6, 0.1, 0]), 1.0, 0.3);
  assert.equal(hits.length, 1);
  assert.equal(hits[0].frameIndex, 3);
  assert.equal(hits[0].side, "RIGHT");
});

test("merges peaks within refractory period, keeping the highest", () => {
  const hits = detectHits(features([0, 2.0, 1.8, 2.2, 0.1, 0]), 1.0, 0.3);
  assert.equal(hits.length, 1);
  assert.equal(hits[0].frameIndex, 3);
});

test("separate swings outside refractory are both kept", () => {
  const hits = detectHits(features([0, 2.0, 0, 0, 0, 2.0, 0]), 1.0, 0.3);
  assert.equal(hits.length, 2);
});

test("no hits below threshold", () => {
  assert.deepEqual(detectHits(features([0, 0.3, 0.4, 0.2]), 1.0, 0.3), []);
});

test("null frames are skipped", () => {
  const f = [
    null,
    null,
    {
      t: 0.2,
      leftWristSpeed: 0,
      rightWristSpeed: 2.0,
      get dominantSide() {
        return "RIGHT";
      },
      get dominantSpeed() {
        return 2.0;
      },
    },
    null,
  ];
  const hits = detectHits(f, 1.0, 0.3);
  assert.equal(hits.length, 1);
});
