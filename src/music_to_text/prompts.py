"""Prompt templates for music-to-text generation."""

from __future__ import annotations

import json

from music_to_text.schemas import AudioFeatures, HeuristicTags, OutputMode


def build_prompt(features: AudioFeatures, tags: HeuristicTags, mode: OutputMode) -> str:
    payload = {
        "mode": mode,
        "features": features.model_dump(),
        "heuristic_tags": tags.model_dump(),
    }
    return (
        "You are a music intelligence assistant. Convert the provided audio-analysis "
        "metadata into useful music-industry language. Return concise JSON with keys: "
        "short_description, detailed_ar_description, pr_pitch, playlist_pitch, "
        "sync_licensing_pitch, genre_tags, mood_tags, instrument_production_tags.\n\n"
        f"Analysis metadata:\n{json.dumps(payload, indent=2)}"
    )

