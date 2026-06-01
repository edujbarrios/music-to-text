from music_to_text.schemas import AudioFeatures, HeuristicTags


def test_audio_feature_schema_accepts_core_metadata() -> None:
    features = AudioFeatures(
        path="song.wav",
        duration_seconds=120.0,
        sample_rate=44100,
        tempo_bpm=118.0,
        loudness_proxy_db=-16.5,
        spectral_centroid_mean=2400.0,
        chroma_mean=[0.1] * 12,
        key_estimate="C major/minor estimate",
        onset_strength_mean=1.2,
        energy_profile=[0.2, 0.5, 1.0],
        section_changes_seconds=[30.0, 64.0],
    )

    assert features.tempo_bpm == 118.0


def test_heuristic_schema_defaults_are_empty_lists() -> None:
    tags = HeuristicTags()

    assert tags.mood_tags == []
    assert tags.genre_hints == []
    assert tags.production_descriptors == []

