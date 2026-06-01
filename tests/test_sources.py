from pathlib import Path

from music_to_text.sources import is_supported_url, resolve_audio_source


def test_detects_supported_music_urls() -> None:
    assert is_supported_url("https://www.youtube.com/watch?v=abc123")
    assert is_supported_url("https://youtu.be/abc123")
    assert is_supported_url("https://soundcloud.com/artist/track")


def test_local_paths_are_resolved_without_download() -> None:
    resolved = resolve_audio_source(Path("song.wav"))

    assert resolved.source_type == "file"
    assert resolved.local_path == Path("song.wav")

