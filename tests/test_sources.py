from pathlib import Path

from music_to_text.sources import collect_audio_files, is_supported_url, resolve_audio_source


def test_detects_supported_music_urls() -> None:
    assert is_supported_url("https://www.youtube.com/watch?v=abc123")
    assert is_supported_url("https://youtu.be/abc123")
    assert is_supported_url("https://soundcloud.com/artist/track")


def test_local_paths_are_resolved_without_download() -> None:
    resolved = resolve_audio_source(Path("song.wav"))

    assert resolved.source_type == "file"
    assert resolved.local_path == Path("song.wav")


def test_collect_audio_files_filters_and_sorts(tmp_path) -> None:
    (tmp_path / "b.mp3").write_bytes(b"fake")
    (tmp_path / "a.wav").write_bytes(b"fake")
    (tmp_path / "cover.png").write_bytes(b"fake")

    files = collect_audio_files(tmp_path)

    assert [path.name for path in files] == ["a.wav", "b.mp3"]
