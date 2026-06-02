"""Executable Billie Jean YouTube + llm7.io example.

Run from the repository root:

    python examples/billiejean_example.py

The script writes the analysis result to `examples/billiejean_example.json`.
"""

from __future__ import annotations

from pathlib import Path

from music_to_text import MusicToText

BILLIE_JEAN_YOUTUBE_URL = "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
OUTPUT_PATH = Path(__file__).with_name("billiejean_example.json")
LLM_BASE_URL = "https://api.llm7.io/v1"
LLM_MODEL = "gpt-4o-mini"
LLM_API_KEY = "unused"


def main() -> None:
    analyzer = MusicToText(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        model=LLM_MODEL,
    )
    result = analyzer.analyze(BILLIE_JEAN_YOUTUBE_URL, mode="json")
    OUTPUT_PATH.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    print(f"Wrote Billie Jean analysis JSON to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
