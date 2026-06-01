"""Command line interface for music-to-text."""

from __future__ import annotations

import json
from typing import Annotated
from pathlib import Path

import typer
from rich.console import Console
from rich.json import JSON

from music_to_text.core import MusicToText
from music_to_text.schemas import OutputMode

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
) -> None:
    analyzer = MusicToText(model=model, base_url=base_url, api_key=api_key)
    result = analyzer.analyze(source, mode=mode, no_llm=no_llm, download_dir=download_dir)
    indent = 2 if pretty or mode == "json" else None
    payload = result.model_dump(mode="json")
    text = json.dumps(payload, indent=indent)

    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"Wrote analysis to {output}")
        return

    if pretty or mode == "json":
        console.print(JSON(text))
    else:
        console.print(result.generated_text.short_description)


if __name__ == "__main__":
    app()
