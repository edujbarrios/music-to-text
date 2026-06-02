"""Command line interface for music-to-text."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.json import JSON

from music_to_text.core import MusicToText
from music_to_text.formatters import OutputFormat, format_result
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
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Output format for stdout or --output."),
    ] = "text",
    download_dir: Annotated[
        Path | None,
        typer.Option("--download-dir", help="Keep URL downloads in this directory instead of a temporary folder."),
    ] = None,
    cookies: Annotated[
        Path | None,
        typer.Option("--cookies", help="Path to a cookies.txt file for yt-dlp URL downloads."),
    ] = None,
    cookies_from_browser: Annotated[
        str | None,
        typer.Option("--cookies-from-browser", help="Browser cookies for yt-dlp, e.g. chrome, edge, firefox, or chrome:Profile 1."),
    ] = None,
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Analyze audio files recursively when SOURCE is a directory.")] = False,
) -> None:
    analyzer = MusicToText(model=model, base_url=base_url, api_key=api_key)
    source_path = Path(source)
    if source_path.is_dir():
        results = analyzer.analyze_many(source_path, mode=mode, no_llm=no_llm, recursive=recursive)
        _write_or_print(results, mode=mode, output=output, pretty=pretty, output_format=output_format)
        return

    result = analyzer.analyze(
        source,
        mode=mode,
        no_llm=no_llm,
        download_dir=download_dir,
        cookies=cookies,
        cookies_from_browser=cookies_from_browser,
    )
    _write_or_print(result, mode=mode, output=output, pretty=pretty, output_format=output_format)


def _write_or_print(
    result: AnalysisResult | list[AnalysisResult],
    mode: OutputMode,
    output: Path | None,
    pretty: bool,
    output_format: OutputFormat,
) -> None:
    resolved_format: OutputFormat = "json" if mode == "json" else output_format
    text = format_result(result, output_format=resolved_format, pretty=pretty or mode == "json")

    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"Wrote analysis to {output}")
        return

    if resolved_format == "json":
        console.print(JSON(text))
    else:
        console.print(text)


if __name__ == "__main__":
    app()
