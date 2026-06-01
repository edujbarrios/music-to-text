"""Deterministic tags and local text derived from audio features."""

from __future__ import annotations

from music_to_text.schemas import AudioFeatures, GeneratedText, HeuristicTags, OutputMode


def build_heuristic_tags(features: AudioFeatures) -> HeuristicTags:
    mood_tags: list[str] = []
    genre_hints: list[str] = []
    production: list[str] = []

    if features.tempo_bpm >= 135:
        mood_tags.extend(["energetic", "urgent"])
        genre_hints.extend(["dance", "electronic"])
    elif features.tempo_bpm >= 105:
        mood_tags.extend(["driving", "upbeat"])
        genre_hints.extend(["pop", "indie"])
    elif features.tempo_bpm >= 75:
        mood_tags.extend(["steady", "mid-tempo"])
        genre_hints.extend(["singer-songwriter", "alternative"])
    else:
        mood_tags.extend(["slow", "reflective"])
        genre_hints.extend(["ambient", "ballad"])

    if features.spectral_centroid_mean > 3000:
        production.extend(["bright", "crisp top end"])
    elif features.spectral_centroid_mean < 1400:
        production.extend(["warm", "dark tone"])
    else:
        production.append("balanced spectrum")

    if features.loudness_proxy_db > -18:
        energy_label = "high"
        production.append("forward loudness")
    elif features.loudness_proxy_db > -28:
        energy_label = "medium"
        production.append("moderate dynamics")
    else:
        energy_label = "low"
        production.append("wide or quiet dynamics")

    if features.onset_strength_mean > 1.5:
        mood_tags.append("rhythmic")
        production.append("strong transients")

    return HeuristicTags(
        mood_tags=_dedupe(mood_tags),
        genre_hints=_dedupe(genre_hints),
        production_descriptors=_dedupe(production),
        energy_label=energy_label,
    )


def generate_local_text(features: AudioFeatures, tags: HeuristicTags, mode: OutputMode) -> GeneratedText:
    base = (
        f"This track is an approximately {features.duration_seconds:.1f}s piece around "
        f"{features.tempo_bpm:.0f} BPM, with a {tags.energy_label}-energy profile, "
        f"{features.key_estimate}, and {', '.join(tags.mood_tags[:3])} character."
    )
    ar = (
        f"A&R notes: the recording suggests {', '.join(tags.genre_hints)} territory with "
        f"{', '.join(tags.production_descriptors)}. Section-change estimates appear near "
        f"{features.section_changes_seconds or 'no strong detected boundaries'} seconds."
    )
    pr = f"PR pitch: a {', '.join(tags.mood_tags[:2])} track with {tags.energy_label} energy and accessible {features.tempo_bpm:.0f} BPM momentum."
    playlist = f"Playlist pitch: recommended for {', '.join(tags.mood_tags)} playlists with hints of {', '.join(tags.genre_hints)}."
    sync = f"Sync pitch: useful for scenes needing {', '.join(tags.mood_tags[:3])} movement and {', '.join(tags.production_descriptors[:2])}."

    return GeneratedText(
        short_description=base,
        detailed_ar_description=ar if mode in {"ar", "summary", "json"} else None,
        pr_pitch=pr if mode in {"pr", "summary", "json"} else None,
        playlist_pitch=playlist if mode in {"playlist", "summary", "json"} else None,
        sync_licensing_pitch=sync if mode in {"sync", "summary", "json"} else None,
    )


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
