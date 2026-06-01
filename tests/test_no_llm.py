from pathlib import Path

from music_to_text.core import MusicToText
from music_to_text.schemas import AudioFeatures
from music_to_text.sources import ResolvedAudioSource


def test_no_llm_analysis_does_not_call_client(monkeypatch) -> None:
    features = AudioFeatures(
        path="song.wav",
        duration_seconds=90.0,
        sample_rate=44100,
        tempo_bpm=122.0,
        loudness_proxy_db=-14.0,
        spectral_centroid_mean=2600.0,
        chroma_mean=[0.2] * 12,
        key_estimate="A major/minor estimate",
        onset_strength_mean=1.0,
        energy_profile=[0.4, 0.8, 1.0],
        section_changes_seconds=[32.0],
    )

    class FailingClient:
        def complete_json(self, prompt: str) -> dict[str, object]:
            raise AssertionError("LLM client should not be called")

    monkeypatch.setattr("music_to_text.core.analyze_audio", lambda path: features)

    analyzer = MusicToText(api_key=None, client=FailingClient())
    result = analyzer.analyze(Path("song.wav"), mode="summary", no_llm=True)

    assert result.llm_used is False
    assert result.generated_text.short_description
    assert result.genre_tags


def test_url_analysis_uses_resolved_download_without_network(monkeypatch, tmp_path) -> None:
    downloaded = tmp_path / "track.m4a"
    downloaded.write_bytes(b"fake")
    features = AudioFeatures(
        path=str(downloaded),
        duration_seconds=60.0,
        sample_rate=44100,
        tempo_bpm=96.0,
        loudness_proxy_db=-20.0,
        spectral_centroid_mean=1800.0,
        chroma_mean=[0.1] * 12,
        key_estimate="D major/minor estimate",
        onset_strength_mean=0.8,
        energy_profile=[0.5, 1.0],
        section_changes_seconds=[],
    )

    class FailingClient:
        def complete_json(self, prompt: str) -> dict[str, object]:
            raise AssertionError("LLM client should not be called")

    monkeypatch.setattr(
        "music_to_text.core.resolve_audio_source",
        lambda source, download_dir=None: ResolvedAudioSource(
            original=str(source),
            local_path=downloaded,
            source_type="url",
            metadata={"title": "Test track", "webpage_url": str(source)},
        ),
    )
    monkeypatch.setattr("music_to_text.core.analyze_audio", lambda path: features)

    analyzer = MusicToText(api_key=None, client=FailingClient())
    result = analyzer.analyze("https://soundcloud.com/artist/track", mode="summary", no_llm=True)

    assert result.source_path == "https://soundcloud.com/artist/track"
    assert result.extra["source_type"] == "url"
    assert result.extra["source_metadata"]["title"] == "Test track"


def test_analyze_many_processes_supported_audio_files(monkeypatch, tmp_path) -> None:
    first = tmp_path / "a.wav"
    second = tmp_path / "b.mp3"
    ignored = tmp_path / "notes.txt"
    first.write_bytes(b"fake")
    second.write_bytes(b"fake")
    ignored.write_text("not audio", encoding="utf-8")

    class FailingClient:
        def complete_json(self, prompt: str) -> dict[str, object]:
            raise AssertionError("LLM client should not be called")

    def fake_analyze_audio(path: Path) -> AudioFeatures:
        return AudioFeatures(
            path=str(path),
            duration_seconds=30.0,
            sample_rate=44100,
            tempo_bpm=110.0,
            loudness_proxy_db=-18.0,
            spectral_centroid_mean=2200.0,
            chroma_mean=[0.1] * 12,
            key_estimate="C major/minor estimate",
            onset_strength_mean=1.0,
            energy_profile=[1.0],
            section_changes_seconds=[],
        )

    monkeypatch.setattr("music_to_text.core.analyze_audio", fake_analyze_audio)

    analyzer = MusicToText(api_key=None, client=FailingClient())
    results = analyzer.analyze_many(tmp_path, no_llm=True)

    assert [Path(result.source_path).name for result in results] == ["a.wav", "b.mp3"]
