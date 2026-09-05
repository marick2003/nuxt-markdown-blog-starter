import { extractPoseFrames } from "./pose.js";
import { analyzeFrames } from "./pipeline/index.js";

const SHOT_COLORS = {
  forehand: getCssVar("--forehand"),
  backhand: getCssVar("--backhand"),
  serve: getCssVar("--serve"),
  unknown: getCssVar("--unknown"),
};
const SHOT_LABELS_ZH = { forehand: "正手", backhand: "反手", serve: "發球", unknown: "未辨識" };

function getCssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

const drop = document.getElementById("drop");
const fileInput = document.getElementById("file-input");
const filenameEl = document.getElementById("filename");
const analyzeBtn = document.getElementById("analyze-btn");
const statusEl = document.getElementById("status");
const progressWrap = document.getElementById("progress-wrap");
const progressBar = document.getElementById("progress-bar");
const resultsEl = document.getElementById("results");

let selectedFile = null;
let barChart = null;
let timelineChart = null;

drop.addEventListener("click", () => fileInput.click());
["dragover", "dragenter"].forEach((evt) =>
  drop.addEventListener(evt, (e) => {
    e.preventDefault();
    drop.classList.add("drag");
  })
);
["dragleave", "drop"].forEach((evt) =>
  drop.addEventListener(evt, (e) => {
    e.preventDefault();
    drop.classList.remove("drag");
  })
);
drop.addEventListener("drop", (e) => {
  const f = e.dataTransfer.files[0];
  if (f) setFile(f);
});
fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});

function setFile(file) {
  selectedFile = file;
  filenameEl.textContent = file.name;
  analyzeBtn.disabled = false;
  statusEl.textContent = "";
  statusEl.classList.remove("error");
}

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  analyzeBtn.disabled = true;
  statusEl.classList.remove("error");
  statusEl.textContent = "載入分析模型中...";
  resultsEl.classList.add("hidden");
  progressWrap.classList.remove("hidden");
  progressBar.style.width = "0%";

  try {
    const { frames, timestamps } = await extractPoseFrames(selectedFile, {
      onProgress: (t, duration) => {
        const pct = Math.min(100, Math.round((t / duration) * 100));
        progressBar.style.width = `${pct}%`;
        statusEl.textContent = `分析中... ${pct}%`;
      },
    });

    const { stats, duration } = analyzeFrames(frames, timestamps);
    renderResults(stats, duration);
    statusEl.textContent = "分析完成(全部在你的瀏覽器裡執行,影片不會上傳到任何伺服器)";
  } catch (err) {
    console.error(err);
    statusEl.textContent = `發生錯誤:${err.message}`;
    statusEl.classList.add("error");
  } finally {
    analyzeBtn.disabled = false;
    progressWrap.classList.add("hidden");
  }
});

function renderResults(stats, duration) {
  document.getElementById("stat-duration").textContent = `${duration.toFixed(1)}s`;
  document.getElementById("stat-rallies").textContent = stats.rallyCount;
  document.getElementById("stat-shots").textContent = stats.shots.length;

  const types = ["forehand", "backhand", "serve", "unknown"].filter((t) => stats.shotCounts[t]);
  const counts = types.map((t) => stats.shotCounts[t]);
  const colors = types.map((t) => SHOT_COLORS[t]);
  const zhLabels = types.map((t) => `${SHOT_LABELS_ZH[t]} ${t}`);

  if (barChart) barChart.destroy();
  barChart = new Chart(document.getElementById("bar-chart"), {
    type: "bar",
    data: { labels: zhLabels, datasets: [{ data: counts, backgroundColor: colors, borderRadius: 6 }] },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#8b93a7" }, grid: { display: false } },
        y: { beginAtZero: true, ticks: { color: "#8b93a7", precision: 0 }, grid: { color: "#262f45" } },
      },
    },
  });

  if (timelineChart) timelineChart.destroy();
  const points = stats.shots.map((s) => ({ x: s.t, y: s.rallyIndex, backgroundColor: SHOT_COLORS[s.shotType] }));
  timelineChart = new Chart(document.getElementById("timeline-chart"), {
    type: "scatter",
    data: {
      datasets: [
        {
          data: points,
          pointBackgroundColor: points.map((p) => p.backgroundColor),
          pointRadius: 6,
        },
      ],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: {
          title: { display: true, text: "時間 (秒)", color: "#8b93a7" },
          ticks: { color: "#8b93a7" },
          grid: { color: "#262f45" },
        },
        y: {
          title: { display: true, text: "回合 Rally #", color: "#8b93a7" },
          ticks: { color: "#8b93a7", precision: 0, stepSize: 1 },
          grid: { color: "#262f45" },
        },
      },
    },
  });

  resultsEl.classList.remove("hidden");
}
