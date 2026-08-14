from pathlib import Path

import pytest

from music_to_text.sources import (
    DEFAULT_YOUTUBE_PLAYER_CLIENT,
    SUPPORTED_AUDIO_EXTENSIONS,
    _postprocessed_audio_path,
    _is_youtube_url,
    _parse_cookies_from_browser,
    collect_audio_files,
    is_supported_url,
    resolve_audio_source,
)


def test_detects_supported_music_urls() -> None:
    assert is_supported_url("https://www.youtube.com/watch?v=abc123")
    assert is_supported_url("https://youtu.be/abc123")
    assert is_supported_url("https://soundcloud.com/artist/track")


def test_local_paths_are_resolved_without_download() -> None:
    resolved = resolve_audio_source(Path("song.wav"))

    assert resolved.source_type == "file"
    assert resolved.local_path == Path("song.wav")


def test_unsupported_web_url_has_actionable_error() -> None:
    with pytest.raises(ValueError, match="Supported providers are YouTube and SoundCloud"):
        resolve_audio_source("https://example.com/song.mp3")


def test_collect_audio_files_filters_and_sorts(tmp_path) -> None:
    (tmp_path / "b.mp3").write_bytes(b"fake")
    (tmp_path / "a.opus").write_bytes(b"fake")
    (tmp_path / "cover.png").write_bytes(b"fake")

    files = collect_audio_files(tmp_path)

    assert [path.name for path in files] == ["a.opus", "b.mp3"]


def test_supported_audio_extensions_cover_common_catalog_formats() -> None:
    assert {".aac", ".aiff", ".ogg", ".opus", ".wma"}.issubset(SUPPORTED_AUDIO_EXTENSIONS)


def test_parse_cookies_from_browser() -> None:
    assert _parse_cookies_from_browser("chrome") == ("chrome", None, None, None)
    assert _parse_cookies_from_browser("chrome:Profile 1") == ("chrome", "Profile 1", None, None)


def test_detects_youtube_urls_for_android_player_fallback() -> None:
    assert DEFAULT_YOUTUBE_PLAYER_CLIENT == "android"
    assert _is_youtube_url("https://www.youtube.com/watch?v=abc123")
    assert _is_youtube_url("https://youtu.be/abc123")
    assert not _is_youtube_url("https://soundcloud.com/artist/track")


def test_postprocessed_audio_path_prefers_wav(tmp_path) -> None:
    original = tmp_path / "track.mp4"
    wav = tmp_path / "track.wav"
    original.write_bytes(b"fake mp4")
    wav.write_bytes(b"fake wav")

    assert _postprocessed_audio_path(original) == wav
