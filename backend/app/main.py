"""FastAPI backend for squash video analysis."""
from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import AnalysisResult, ShotOut
from .pipeline import analyze_video

app = FastAPI(title="Squash Video Analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if _FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="static")

_ALLOWED_SUFFIXES = (".mp4", ".mov", ".avi", ".mkv")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze(file: UploadFile = File(...)) -> AnalysisResult:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_SUFFIXES:
        raise HTTPException(400, f"unsupported file type; expected one of {_ALLOWED_SUFFIXES}")

    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        stats, duration = analyze_video(tmp.name)

    return AnalysisResult(
        duration_seconds=duration,
        rally_count=stats.rally_count,
        shot_counts=stats.shot_counts,
        shots=[ShotOut(t=s.t, side=s.side, shot_type=s.shot_type, rally_index=s.rally_index) for s in stats.shots],
    )
