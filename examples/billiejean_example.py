"""Executable Billie Jean YouTube + llm7.io example.

Run from the repository root:

    python examples/billiejean_example.py

The script writes the analysis result to `examples/billiejean_example.json`.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path

from dotenv import load_dotenv

from music_to_text import MusicToText

load_dotenv()

BILLIE_JEAN_YOUTUBE_URL = "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
OUTPUT_PATH = Path(__file__).with_name("billiejean_example.json")
DOWNLOAD_DIR = Path(__file__).with_name("_downloads")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.llm7.io/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_API_KEY = os.getenv("LLM_API_KEY", "unused")
DEFAULT_BROWSER_COOKIE_SOURCES = ("chrome", "edge", "firefox")
BILLIE_JEAN_AUDIO_PATH_ENV = "BILLIE_JEAN_AUDIO_PATH"


def run() -> None:
    _suppress_noisy_dependency_warnings()
    analyzer = MusicToText(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        model=LLM_MODEL,
    )
    result = _analyze_with_cookie_fallbacks(analyzer)
    OUTPUT_PATH.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    print(f"Wrote Billie Jean analysis JSON to {OUTPUT_PATH}")


def _suppress_noisy_dependency_warnings() -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"paramiko\..*")
    warnings.filterwarnings("ignore", message=".*TripleDES.*")
    warnings.filterwarnings("ignore", message=".*Blowfish.*")


def main() -> int:
    try:
        run()
    except RuntimeError as exc:
        print(exc)
        return 1
    return 0


def _analyze_with_cookie_fallbacks(analyzer: MusicToText):
    try:
        from yt_dlp.utils import DownloadError
    except ImportError:
        DownloadError = RuntimeError

    cookies = os.getenv("YTDLP_COOKIES")
    local_audio_path = os.getenv(BILLIE_JEAN_AUDIO_PATH_ENV)
    browser_cookie_sources = _browser_cookie_sources()
    last_error: Exception | None = None

    if local_audio_path:
        print(f"Using local Billie Jean audio file: {local_audio_path}")
        return _analyze_with_llm_fallback(analyzer, local_audio_path)

    if cookies:
        try:
            return _analyze_with_llm_fallback(analyzer, BILLIE_JEAN_YOUTUBE_URL, cookies=cookies)
        except DownloadError as exc:
            last_error = exc
            print(f"cookies file failed, trying YouTube fallback next: {cookies}")

    try:
        print("Trying YouTube download with android player client")
        return _analyze_with_llm_fallback(analyzer, BILLIE_JEAN_YOUTUBE_URL)
    except DownloadError as exc:
        last_error = exc
        print("YouTube android player fallback failed, trying browser cookies next")

    for browser in browser_cookie_sources:
        try:
            print(f"Trying YouTube cookies from browser: {browser}")
            return _analyze_with_llm_fallback(
                analyzer,
                BILLIE_JEAN_YOUTUBE_URL,
                cookies_from_browser=browser,
            )
        except DownloadError as exc:
            last_error = exc
            print(f"Browser cookies failed: {browser}")

    raise RuntimeError(_download_help_message()) from last_error


def _browser_cookie_sources() -> tuple[str, ...]:
    configured = os.getenv("YTDLP_COOKIES_FROM_BROWSER")
    if configured:
        return (configured,)
    return DEFAULT_BROWSER_COOKIE_SOURCES


def _analyze_with_llm_fallback(
    analyzer: MusicToText,
    source: str,
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
):
    result = analyzer.analyze(
        source,
        mode="json",
        download_dir=DOWNLOAD_DIR,
        cookies=cookies,
        cookies_from_browser=cookies_from_browser,
        llm_fallback=True,
    )
    if result.extra.get("llm_fallback_used"):
        print(f"LLM request failed ({result.extra['llm_error']}); writing no-LLM analysis instead.")
    result.extra["llm_provider_example"] = {
        "base_url": LLM_BASE_URL,
        "model": LLM_MODEL,
        "api_key_env_var": "LLM_API_KEY",
        "api_key_configured": bool(LLM_API_KEY),
    }
    return result


def _download_help_message() -> str:
    return (
        "Could not download the YouTube audio.\n\n"
        "Try one of these options:\n"
        "1. Close Chrome/Edge completely and rerun the script.\n"
        "2. Force a signed-in browser profile:\n"
        "   PowerShell: $env:YTDLP_COOKIES_FROM_BROWSER='chrome:Profile 1'\n"
        "   Then run:  python examples/billiejean_example.py\n"
        "3. Export YouTube cookies to cookies.txt and run:\n"
        "   PowerShell: $env:YTDLP_COOKIES='C:\\path\\to\\cookies.txt'\n"
        "   Then run:  python examples/billiejean_example.py\n"
        "4. If you already have the audio locally, bypass YouTube:\n"
        "   PowerShell: $env:BILLIE_JEAN_AUDIO_PATH='C:\\path\\to\\billie-jean.mp3'\n"
        "   Then run:  python examples/billiejean_example.py\n"
        "5. Update yt-dlp, then retry:\n"
        "   python -m pip install -U yt-dlp\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
