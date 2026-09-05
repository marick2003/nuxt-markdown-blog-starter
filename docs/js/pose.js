// Browser-side pose extraction via MediaPipe Tasks Vision (WASM), replacing
// the Python backend's app/pipeline/pose.py + video_io.py. Runs entirely
// client-side, which is what makes this page deployable as static content
// (e.g. GitHub Pages) with no server.
import { FilesetResolver, PoseLandmarker } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14";
import * as config from "./pipeline/config.js";

// Subset of MediaPipe's 33 pose landmarks that the pipeline actually uses.
const LANDMARK_NAMES = {
  0: "NOSE",
  11: "LEFT_SHOULDER",
  12: "RIGHT_SHOULDER",
  13: "LEFT_ELBOW",
  14: "RIGHT_ELBOW",
  15: "LEFT_WRIST",
  16: "RIGHT_WRIST",
  23: "LEFT_HIP",
  24: "RIGHT_HIP",
};

let landmarkerPromise = null;

function getLandmarker() {
  if (!landmarkerPromise) {
    landmarkerPromise = (async () => {
      const vision = await FilesetResolver.forVisionTasks(`${config.TASKS_VISION_CDN}/wasm`);
      return PoseLandmarker.createFromOptions(vision, {
        baseOptions: { modelAssetPath: config.MODEL_URL },
        runningMode: "VIDEO",
        numPoses: 1,
      });
    })();
  }
  return landmarkerPromise;
}

function seekTo(video, t) {
  return new Promise((resolve) => {
    const onSeeked = () => {
      video.removeEventListener("seeked", onSeeked);
      resolve();
    };
    video.addEventListener("seeked", onSeeked);
    video.currentTime = t;
  });
}

function toFrame(result) {
  if (!result.landmarks || result.landmarks.length === 0) return null;
  const landmarks = result.landmarks[0];
  const frame = {};
  for (const [idx, name] of Object.entries(LANDMARK_NAMES)) {
    const lm = landmarks[Number(idx)];
    frame[name] = [lm.x, lm.y, lm.visibility ?? 1];
  }
  return frame;
}

/**
 * Decode a video file in the browser, sample it at `sampleFps`, and run
 * pose detection on each sampled frame.
 *
 * Returns `{ frames, timestamps }`, matching the shape
 * `analyzeFrames` in pipeline/index.js expects.
 */
export async function extractPoseFrames(file, { sampleFps = config.SAMPLE_FPS, onProgress } = {}) {
  const landmarker = await getLandmarker();

  const video = document.createElement("video");
  video.muted = true;
  video.playsInline = true;
  video.preload = "auto";
  video.src = URL.createObjectURL(file);

  try {
    await new Promise((resolve, reject) => {
      video.onloadedmetadata = () => resolve();
      video.onerror = () => reject(new Error("無法讀取此影片檔案"));
    });

    const duration = video.duration;
    if (!isFinite(duration) || duration <= 0) {
      throw new Error("無法取得影片長度");
    }

    const step = 1 / sampleFps;
    const frames = [];
    const timestamps = [];

    let lastMs = -1;
    for (let t = 0; t < duration; t += step) {
      await seekTo(video, t);

      let ms = Math.round(t * 1000);
      if (ms <= lastMs) ms = lastMs + 1;
      lastMs = ms;

      const result = landmarker.detectForVideo(video, ms);
      frames.push(toFrame(result));
      timestamps.push(t);

      if (onProgress) onProgress(t, duration);
    }

    return { frames, timestamps };
  } finally {
    URL.revokeObjectURL(video.src);
  }
}
