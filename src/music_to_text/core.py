"""Public MusicToText analysis API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from requests import RequestException

from music_to_text.audio import analyze_audio
from music_to_text.heuristics import build_heuristic_tags, generate_local_text
from music_to_text.llm import LLMConfig, OpenAICompatibleClient
from music_to_text.prompts import build_prompt
from music_to_text.schemas import AnalysisResult, GeneratedText, OutputMode
from music_to_text.sources import collect_audio_files, resolve_audio_source


class MusicToText:
    """Analyze music files and produce structured metadata plus descriptions."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        client: OpenAICompatibleClient | None = None,
    ) -> None:
        env_config = LLMConfig.from_env()
        self.config = LLMConfig(
            api_key=api_key or env_config.api_key,
            base_url=base_url or env_config.base_url,
            model=model or env_config.model,
        )
        self.client = client or OpenAICompatibleClient(self.config)

    def analyze(
        self,
        source: str | Path,
        mode: OutputMode = "summary",
        no_llm: bool = False,
        download_dir: str | Path | None = None,
        cookies: str | Path | None = None,
        cookies_from_browser: str | None = None,
        llm_fallback: bool = False,
    ) -> AnalysisResult:
        resolved_source = resolve_audio_source(
            source,
            download_dir=download_dir,
            cookies=cookies,
            cookies_from_browser=cookies_from_browser,
        )
        try:
            features = analyze_audio(resolved_source.local_path)
            heuristic_tags = build_heuristic_tags(features)
            local_text = generate_local_text(features, heuristic_tags, mode)
            genre_tags = heuristic_tags.genre_hints
            mood_tags = heuristic_tags.mood_tags
            production_tags = heuristic_tags.production_descriptors
            generated_text = local_text
            llm_used = False
            extra: dict[str, Any] = {
                "source_type": resolved_source.source_type,
                "resolved_path": str(resolved_source.local_path),
            }
            if resolved_source.metadata:
                extra["source_metadata"] = resolved_source.metadata

            if not no_llm:
                prompt = build_prompt(features, heuristic_tags, mode)
                try:
                    llm_payload = self.client.complete_json(prompt)
                except (RequestException, ValueError) as exc:
                    if not llm_fallback:
                        raise
                    extra["llm_error"] = str(exc)
                    extra["llm_fallback_used"] = True
                else:
                    generated_text = GeneratedText(
                        short_description=llm_payload.get("short_description") or local_text.short_description,
                        detailed_ar_description=llm_payload.get("detailed_ar_description") or local_text.detailed_ar_description,
                        pr_pitch=llm_payload.get("pr_pitch") or local_text.pr_pitch,
                        playlist_pitch=llm_payload.get("playlist_pitch") or local_text.playlist_pitch,
                        sync_licensing_pitch=llm_payload.get("sync_licensing_pitch") or local_text.sync_licensing_pitch,
                    )
                    genre_tags = _list_or_default(llm_payload.get("genre_tags"), genre_tags)
                    mood_tags = _list_or_default(llm_payload.get("mood_tags"), mood_tags)
                    production_tags = _list_or_default(llm_payload.get("instrument_production_tags"), production_tags)
                    extra["llm_raw"] = llm_payload
                    llm_used = True

            return AnalysisResult(
                source_path=resolved_source.original,
                mode=mode,
                features=features,
                heuristic_tags=heuristic_tags,
                generated_text=generated_text,
                genre_tags=genre_tags,
                mood_tags=mood_tags,
                instrument_production_tags=production_tags,
                llm_used=llm_used,
                model=self.config.model if llm_used else None,
                extra=extra,
            )
        finally:
            resolved_source.cleanup()

    def analyze_many(
        self,
        directory: str | Path,
        mode: OutputMode = "summary",
        no_llm: bool = False,
        recursive: bool = False,
        limit: int | None = None,
        llm_fallback: bool = False,
    ) -> list[AnalysisResult]:
        """Analyze all supported audio files in a local directory."""

        files = collect_audio_files(directory, recursive=recursive)
        if limit is not None:
            if limit < 1:
                raise ValueError("limit must be greater than zero")
            files = files[:limit]
        return [self.analyze(path, mode=mode, no_llm=no_llm, llm_fallback=llm_fallback) for path in files]


def _list_or_default(value: object, default: list[str]) -> list[str]:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return default
