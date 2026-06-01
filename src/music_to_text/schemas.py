"""Typed result models for music analysis."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

OutputMode = Literal["summary", "ar", "pr", "playlist", "sync", "json"]


class AudioFeatures(BaseModel):
    path: str
    duration_seconds: float = Field(ge=0)
    sample_rate: int = Field(gt=0)
    tempo_bpm: float = Field(ge=0)
    loudness_proxy_db: float
    spectral_centroid_mean: float = Field(ge=0)
    chroma_mean: list[float] = Field(default_factory=list)
    key_estimate: str
    onset_strength_mean: float = Field(ge=0)
    energy_profile: list[float] = Field(default_factory=list)
    section_changes_seconds: list[float] = Field(default_factory=list)


class HeuristicTags(BaseModel):
    mood_tags: list[str] = Field(default_factory=list)
    genre_hints: list[str] = Field(default_factory=list)
    production_descriptors: list[str] = Field(default_factory=list)
    energy_label: str = "unknown"


class GeneratedText(BaseModel):
    short_description: str
    detailed_ar_description: str | None = None
    pr_pitch: str | None = None
    playlist_pitch: str | None = None
    sync_licensing_pitch: str | None = None


class AnalysisResult(BaseModel):
    source_path: str
    mode: OutputMode
    features: AudioFeatures
    heuristic_tags: HeuristicTags
    generated_text: GeneratedText
    genre_tags: list[str] = Field(default_factory=list)
    mood_tags: list[str] = Field(default_factory=list)
    instrument_production_tags: list[str] = Field(default_factory=list)
    llm_used: bool = False
    model: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

