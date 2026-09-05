import test from "node:test";
import assert from "node:assert/strict";
import { SHOT_BACKHAND, SHOT_FOREHAND, SHOT_SERVE, SHOT_UNKNOWN, classifyShot } from "../js/pipeline/classifier.js";

function frame(rightWristX, rightWristY = 0.5, shoulderY = 0.3) {
  return {
    RIGHT_SHOULDER: [0.6, shoulderY, 0.9],
    LEFT_SHOULDER: [0.4, shoulderY, 0.9],
    RIGHT_WRIST: [rightWristX, rightWristY, 0.9],
    LEFT_WRIST: [0.3, 0.6, 0.9],
    LEFT_HIP: [0.45, 0.6, 0.9],
    RIGHT_HIP: [0.55, 0.6, 0.9],
  };
}

test("forehand when wrist stays on same side", () => {
  assert.equal(classifyShot(frame(0.7), "RIGHT", false), SHOT_FOREHAND);
});

test("backhand when wrist crosses midline", () => {
  assert.equal(classifyShot(frame(0.3), "RIGHT", false), SHOT_BACKHAND);
});

test("serve when first hit and contact above shoulder", () => {
  assert.equal(classifyShot(frame(0.7, 0.1, 0.3), "RIGHT", true), SHOT_SERVE);
});

test("not serve when high contact but not first hit of rally", () => {
  assert.equal(classifyShot(frame(0.7, 0.1, 0.3), "RIGHT", false), SHOT_FOREHAND);
});

test("unknown when landmarks missing", () => {
  assert.equal(classifyShot({ RIGHT_SHOULDER: [0.6, 0.3, 0.9] }, "RIGHT", false), SHOT_UNKNOWN);
});
