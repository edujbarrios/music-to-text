from music_to_text.formatters import format_result
from music_to_text.schemas import AnalysisResult, AudioFeatures, GeneratedText, HeuristicTags


def test_format_result_as_markdown() -> None:
    result = _analysis_result()

    markdown = format_result(result, output_format="markdown")

    assert "# Music-to-Text Analysis" in markdown
    assert "**Source:** `song.wav`" in markdown
    assert "**Model:** `test-model`" in markdown
    assert "**Title:** Example Song" in markdown
    assert "A concise track description." in markdown


def test_format_result_as_csv() -> None:
    result = _analysis_result()

    csv_output = format_result([result], output_format="csv")

    assert "source_path,mode,duration_seconds,sample_rate" in csv_output
    assert "song.wav,summary,42.0,44100,120.0" in csv_output
    assert "True,test-model,file,A concise track description." in csv_output


def _analysis_result() -> AnalysisResult:
    return AnalysisResult(
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
        llm_used=True,
        model="test-model",
        extra={
            "source_type": "file",
            "source_metadata": {
                "title": "Example Song",
                "uploader": "Example Artist",
                "webpage_url": "https://example.com/song",
            },
        },
    )
