"""Executable Billie Jean YouTube + llm7.io example.

Run from the repository root:

    python examples/billiejean_example.py

The script writes the analysis result to `examples/billiejean_example.json`.
"""

from __future__ import annotations

import os
from pathlib import Path

from music_to_text import MusicToText

BILLIE_JEAN_YOUTUBE_URL = "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
OUTPUT_PATH = Path(__file__).with_name("billiejean_example.json")
LLM_BASE_URL = "https://api.llm7.io/v1"
LLM_MODEL = "gpt-4o-mini"
LLM_API_KEY = "unused"
DEFAULT_BROWSER_COOKIE_SOURCES = ("chrome", "edge", "firefox")


def main() -> None:
    analyzer = MusicToText(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        model=LLM_MODEL,
    )
    result = _analyze_with_cookie_fallbacks(analyzer)
    OUTPUT_PATH.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    print(f"Wrote Billie Jean analysis JSON to {OUTPUT_PATH}")


def _analyze_with_cookie_fallbacks(analyzer: MusicToText):
    try:
        from yt_dlp.utils import DownloadError
    except ImportError:
        DownloadError = RuntimeError

    cookies = os.getenv("YTDLP_COOKIES")
    browser_cookie_sources = _browser_cookie_sources()
    last_error: Exception | None = None

    if cookies:
        try:
            return analyzer.analyze(BILLIE_JEAN_YOUTUBE_URL, mode="json", cookies=cookies)
        except DownloadError as exc:
            last_error = exc
            print(f"cookies file failed, trying browser cookies next: {cookies}")

    for browser in browser_cookie_sources:
        try:
            print(f"Trying YouTube cookies from browser: {browser}")
            return analyzer.analyze(
                BILLIE_JEAN_YOUTUBE_URL,
                mode="json",
                cookies_from_browser=browser,
            )
        except DownloadError as exc:
            last_error = exc
            print(f"Browser cookies failed: {browser}")

    raise RuntimeError(
        "Could not download the YouTube audio. Sign in to YouTube in Chrome, Edge, or Firefox, "
        "close the browser if its cookie database is locked, then rerun this script. You can also "
        "set YTDLP_COOKIES to a cookies.txt path or YTDLP_COOKIES_FROM_BROWSER to a value like "
        "'chrome', 'edge', 'firefox', or 'chrome:Profile 1'."
    ) from last_error


def _browser_cookie_sources() -> tuple[str, ...]:
    configured = os.getenv("YTDLP_COOKIES_FROM_BROWSER")
    if configured:
        return (configured,)
    return DEFAULT_BROWSER_COOKIE_SOURCES


if __name__ == "__main__":
    main()
