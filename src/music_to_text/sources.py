"""Input resolution for local files and supported music URLs."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SUPPORTED_URL_HOSTS = (
    "youtube.com",
    "www.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "soundcloud.com",
    "www.soundcloud.com",
    "on.soundcloud.com",
)
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a"}


@dataclass
class ResolvedAudioSource:
    original: str
    local_path: Path
    source_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    _temp_dir: Path | None = None

    def cleanup(self) -> None:
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)


def resolve_audio_source(source: str | Path, download_dir: str | Path | None = None) -> ResolvedAudioSource:
    source_text = str(source)
    if is_supported_url(source_text):
        return download_audio_url(source_text, download_dir=download_dir)

    path = Path(source)
    return ResolvedAudioSource(original=source_text, local_path=path, source_type="file")


def collect_audio_files(directory: str | Path, recursive: bool = False) -> list[Path]:
    """Return supported audio files in a directory with stable ordering."""

    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    candidates = root.rglob("*") if recursive else root.iterdir()
    return sorted(
        path
        for path in candidates
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
    )


def is_supported_url(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.netloc.lower()
    return host in SUPPORTED_URL_HOSTS or host.endswith(".youtube.com") or host.endswith(".soundcloud.com")


def download_audio_url(url: str, download_dir: str | Path | None = None) -> ResolvedAudioSource:
    """Download a YouTube or SoundCloud URL to a local audio file with yt-dlp."""

    try:
        from yt_dlp import YoutubeDL
    except ImportError as exc:
        raise RuntimeError("URL inputs require yt-dlp. Install dependencies with `pip install -e .`.") from exc

    temp_dir: Path | None = None
    if download_dir is None:
        temp_dir = Path(tempfile.mkdtemp(prefix="music-to-text-"))
        target_dir = temp_dir
    else:
        target_dir = Path(download_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

    options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": str(target_dir / "%(title).200B-%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)
        local_path = _downloaded_path(downloader, info)

    if not local_path.exists():
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise FileNotFoundError(f"Downloaded audio file was not found for URL: {url}")

    metadata = {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "webpage_url": info.get("webpage_url") or url,
        "extractor": info.get("extractor"),
        "duration": info.get("duration"),
    }
    return ResolvedAudioSource(
        original=url,
        local_path=local_path,
        source_type="url",
        metadata={key: value for key, value in metadata.items() if value is not None},
        _temp_dir=temp_dir,
    )


def _downloaded_path(downloader: Any, info: dict[str, Any]) -> Path:
    requested_downloads = info.get("requested_downloads") or []
    for item in requested_downloads:
        filepath = item.get("filepath")
        if filepath:
            return Path(filepath)
    return Path(downloader.prepare_filename(info))
