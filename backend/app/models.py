"""Pydantic response models for the analysis API."""
from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel


class AnalyzeUrlRequest(BaseModel):
    url: str


class ShotOut(BaseModel):
    t: float
    side: str
    shot_type: str
    rally_index: int


class AnalysisResult(BaseModel):
    duration_seconds: float
    rally_count: int
    shot_counts: Dict[str, int]
    shots: List[ShotOut]
