"""Command line interface for music-to-text."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.json import JSON

from music_to_text.core import MusicToText
from music_to_text.schemas import AnalysisResult, OutputMode

app = typer.Typer(add_completion=False, help="Analyze music and generate structured text.")
console = Console()


@app.command()
def analyze(
    source: Annotated[str, typer.Argument(help="Local audio path, YouTube URL, or SoundCloud URL.")],
    mode: Annotated[OutputMode, typer.Option("--mode", help="Output mode.")] = "summary",
    model: Annotated[str | None, typer.Option("--model", help="OpenAI-compatible model name.")] = None,
    base_url: Annotated[str | None, typer.Option("--base-url", help="OpenAI-compatible API base URL.")] = None,
    api_key: Annotated[str | None, typer.Option("--api-key", help="API key. Prefer LLM_API_KEY.")] = None,
    no_llm: Annotated[bool, typer.Option("--no-llm", help="Skip LLM calls and use local deterministic text.")] = False,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write JSON result to a file.")] = None,
    pretty: Annotated[bool, typer.Option("--pretty", help="Pretty-print JSON output.")] = False,
    download_dir: Annotated[
        Path | None,
        typer.Option("--download-dir", help="Keep URL downloads in this directory instead of a temporary folder."),
    ] = None,
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Analyze audio files recursively when SOURCE is a directory.")] = False,
) -> None:
    analyzer = MusicToText(model=model, base_url=base_url, api_key=api_key)
    source_path = Path(source)
    if source_path.is_dir():
        results = analyzer.analyze_many(source_path, mode=mode, no_llm=no_llm, recursive=recursive)
        _write_or_print(results, mode=mode, output=output, pretty=pretty)
        return

    result = analyzer.analyze(source, mode=mode, no_llm=no_llm, download_dir=download_dir)
    _write_or_print(result, mode=mode, output=output, pretty=pretty)


def _write_or_print(
    result: AnalysisResult | list[AnalysisResult],
    mode: OutputMode,
    output: Path | None,
    pretty: bool,
) -> None:
    indent = 2 if pretty or mode == "json" else None
    payload = [item.model_dump(mode="json") for item in result] if isinstance(result, list) else result.model_dump(mode="json")
    text = json.dumps(payload, indent=indent)

    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"Wrote analysis to {output}")
        return

    if pretty or mode == "json":
        console.print(JSON(text))
    elif isinstance(result, list):
        for item in result:
            console.print(f"{item.source_path}: {item.generated_text.short_description}")
    else:
        console.print(result.generated_text.short_description)


if __name__ == "__main__":
    app()
