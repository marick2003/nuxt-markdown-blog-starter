#!/usr/bin/env python3
"""CLI entry point: analyze a squash video file and print/save the result.

Usage:
    python scripts/analyze_video.py path/to/match.mp4 [--out result.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import analyze_video  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="path to the squash match video file")
    parser.add_argument("--out", help="write the JSON result to this path instead of stdout")
    args = parser.parse_args()

    stats, duration = analyze_video(args.video)
    result = {
        "duration_seconds": duration,
        "rally_count": stats.rally_count,
        "shot_counts": stats.shot_counts,
        "shots": [vars(s) for s in stats.shots],
    }

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(output)
        print(f"wrote {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
