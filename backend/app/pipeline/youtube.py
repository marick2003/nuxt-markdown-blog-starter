"""Download a YouTube video to a local file for analysis, via yt-dlp.

Deliberately restricted to YouTube hosts only - this exists so someone can
analyze a match they found on YouTube, not to act as a general-purpose
video downloader for arbitrary sites (yt-dlp itself supports thousands of
them, which would be an easy thing to abuse if this endpoint accepted any
URL).
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from yt_dlp import YoutubeDL

ALLOWED_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
}

# Keep downloads small and analysis time bounded - this is a demo endpoint,
# not a general-purpose video fetcher.
MAX_DURATION_SECONDS = 20 * 60
MAX_HEIGHT = 720


class InvalidVideoUrlError(ValueError):
    pass


def is_allowed_youtube_url(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host in ALLOWED_HOSTS


def download_youtube_video(url: str, out_dir: str) -> Path:
    """Download `url` into `out_dir` and return the path to the video file.

    Raises `InvalidVideoUrlError` for a disallowed host, an unavailable
    video, or one longer than `MAX_DURATION_SECONDS`.
    """
    if not is_allowed_youtube_url(url):
        raise InvalidVideoUrlError("只支援 youtube.com / youtu.be 的連結")

    ydl_opts = {
        "format": f"bestvideo[height<={MAX_HEIGHT}]+bestaudio/best[height<={MAX_HEIGHT}]/best",
        "outtmpl": str(Path(out_dir) / "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration") or 0
            if duration > MAX_DURATION_SECONDS:
                raise InvalidVideoUrlError(
                    f"影片長度 {duration}s 超過上限 {MAX_DURATION_SECONDS}s,請換一段較短的片段"
                )
            ydl.download([url])
            filename = Path(ydl.prepare_filename(info))
    except InvalidVideoUrlError:
        raise
    except Exception as exc:  # yt-dlp raises its own DownloadError subclasses
        raise InvalidVideoUrlError(f"無法下載此影片:{exc}") from exc

    # merge_output_format can change the container extension after download.
    if not filename.exists():
        filename = filename.with_suffix(".mp4")
    if not filename.exists():
        raise InvalidVideoUrlError("下載失敗,找不到輸出檔案")
    return filename
