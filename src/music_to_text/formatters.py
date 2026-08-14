"""Output formatters for analysis results."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from music_to_text.schemas import AnalysisResult

OutputFormat = Literal["text", "json", "markdown", "csv"]


def format_result(
    result: AnalysisResult | list[AnalysisResult],
    output_format: OutputFormat = "text",
    pretty: bool = False,
) -> str:
    if output_format == "json":
        indent = 2 if pretty else None
        payload = [item.model_dump(mode="json") for item in result] if isinstance(result, list) else result.model_dump(mode="json")
        return json.dumps(payload, indent=indent, ensure_ascii=False)
    if output_format == "markdown":
        return _format_markdown_many(result) if isinstance(result, list) else _format_markdown(result)
    if output_format == "csv":
        return _format_csv(result if isinstance(result, list) else [result])
    return _format_text_many(result) if isinstance(result, list) else result.generated_text.short_description


def _format_text_many(results: list[AnalysisResult]) -> str:
    return "\n".join(f"{item.source_path}: {item.generated_text.short_description}" for item in results)


def _format_markdown_many(results: list[AnalysisResult]) -> str:
    sections = ["# Music-to-Text Analysis", ""]
    for result in results:
        sections.append(_format_markdown(result, heading_level=2))
        sections.append("")
    return "\n".join(sections).strip()


def _format_markdown(result: AnalysisResult, heading_level: int = 1) -> str:
    heading = "#" * heading_level
    features = result.features
    text = result.generated_text
    lines = [
        f"{heading} Music-to-Text Analysis",
        "",
        f"**Source:** `{result.source_path}`",
        f"**Mode:** `{result.mode}`",
        f"**LLM used:** `{result.llm_used}`",
    ]
    if result.model:
        lines.append(f"**Model:** `{result.model}`")
    if result.extra.get("llm_fallback_used"):
        lines.append("**LLM fallback:** local deterministic text used after an LLM error")
    lines.extend(_format_source_metadata(result))
    lines.extend(
        [
            "",
            "## Description" if heading_level == 1 else "### Description",
            "",
            text.short_description,
            "",
        ]
    )
    optional_sections = [
        ("A&R Notes", text.detailed_ar_description),
        ("PR Pitch", text.pr_pitch),
        ("Playlist Pitch", text.playlist_pitch),
        ("Sync Licensing Pitch", text.sync_licensing_pitch),
    ]
    for title, value in optional_sections:
        if value:
            lines.extend([f"{'##' if heading_level == 1 else '###'} {title}", "", value, ""])

    lines.extend(
        [
            "## Tags" if heading_level == 1 else "### Tags",
            "",
            f"- Genre: {_join_or_dash(result.genre_tags)}",
            f"- Mood: {_join_or_dash(result.mood_tags)}",
            f"- Production: {_join_or_dash(result.instrument_production_tags)}",
            "",
            "## Features" if heading_level == 1 else "### Features",
            "",
            f"- Duration: {features.duration_seconds:.2f}s ({_format_duration(features.duration_seconds)})",
            f"- Tempo: {features.tempo_bpm:.2f} BPM",
            f"- Key estimate: {features.key_estimate}",
            f"- Loudness proxy: {features.loudness_proxy_db:.2f} dB",
            f"- Spectral centroid: {features.spectral_centroid_mean:.2f}",
        ]
    )
    return "\n".join(lines).strip()


def _format_csv(results: list[AnalysisResult]) -> str:
    buffer = io.StringIO()
    fieldnames = [
        "source_path",
        "mode",
        "duration_seconds",
        "duration",
        "sample_rate",
        "tempo_bpm",
        "key_estimate",
        "loudness_proxy_db",
        "spectral_centroid_mean",
        "energy_label",
        "genre_tags",
        "mood_tags",
        "production_tags",
        "llm_used",
        "model",
        "source_type",
        "short_description",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for result in results:
        features = result.features
        writer.writerow(
            {
                "source_path": result.source_path,
                "mode": result.mode,
                "duration_seconds": features.duration_seconds,
                "duration": _format_duration(features.duration_seconds),
                "sample_rate": features.sample_rate,
                "tempo_bpm": features.tempo_bpm,
                "key_estimate": features.key_estimate,
                "loudness_proxy_db": features.loudness_proxy_db,
                "spectral_centroid_mean": features.spectral_centroid_mean,
                "energy_label": result.heuristic_tags.energy_label,
                "genre_tags": ";".join(result.genre_tags),
                "mood_tags": ";".join(result.mood_tags),
                "production_tags": ";".join(result.instrument_production_tags),
                "llm_used": result.llm_used,
                "model": result.model or "",
                "source_type": result.extra.get("source_type", ""),
                "short_description": result.generated_text.short_description,
            }
        )
    return buffer.getvalue().strip()


def _join_or_dash(values: list[str]) -> str:
    return ", ".join(values) if values else "-"


def _format_duration(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    minutes, seconds_part = divmod(total_seconds, 60)
    hours, minutes_part = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes_part:02d}:{seconds_part:02d}"
    return f"{minutes_part}:{seconds_part:02d}"


def _format_source_metadata(result: AnalysisResult) -> list[str]:
    metadata = result.extra.get("source_metadata")
    if not isinstance(metadata, dict):
        return []

    lines = []
    for label, key in (
        ("Title", "title"),
        ("Uploader", "uploader"),
        ("URL", "webpage_url"),
    ):
        value = metadata.get(key)
        if value:
            lines.append(f"**{label}:** {value}")
    return lines
