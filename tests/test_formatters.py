from music_to_text.formatters import format_result
from music_to_text.schemas import AnalysisResult, AudioFeatures, GeneratedText, HeuristicTags


def test_format_result_as_markdown() -> None:
    result = AnalysisResult(
        source_path="song.wav",
        mode="summary",
        features=AudioFeatures(
            path="song.wav",
            duration_seconds=42.0,
            sample_rate=44100,
            tempo_bpm=120.0,
            loudness_proxy_db=-18.0,
            spectral_centroid_mean=2300.0,
            chroma_mean=[0.1] * 12,
            key_estimate="C major/minor estimate",
            onset_strength_mean=1.0,
            energy_profile=[1.0],
            section_changes_seconds=[],
        ),
        heuristic_tags=HeuristicTags(
            mood_tags=["driving"],
            genre_hints=["pop"],
            production_descriptors=["balanced spectrum"],
            energy_label="medium",
        ),
        generated_text=GeneratedText(short_description="A concise track description."),
        genre_tags=["pop"],
        mood_tags=["driving"],
        instrument_production_tags=["balanced spectrum"],
    )

    markdown = format_result(result, output_format="markdown")

    assert "# Music-to-Text Analysis" in markdown
    assert "**Source:** `song.wav`" in markdown
    assert "A concise track description." in markdown
