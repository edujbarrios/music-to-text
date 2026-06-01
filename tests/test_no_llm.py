from pathlib import Path

from music_to_text.core import MusicToText
from music_to_text.schemas import AudioFeatures


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
