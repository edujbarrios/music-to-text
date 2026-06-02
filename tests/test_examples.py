import json
from pathlib import Path

from examples import billiejean_example


def test_billiejean_example_json_is_valid() -> None:
    example_path = Path("examples/billiejean_example.json")

    payload = json.loads(example_path.read_text(encoding="utf-8"))

    assert payload["example_name"] == "billiejean_llm7io_youtube_demo"
    assert payload["source"]["url"] == "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
    assert payload["llm_provider_example"]["base_url"] == "https://api.llm7.io/v1"
    assert "with_llm" in payload["command"]


def test_billiejean_example_script_configuration() -> None:
    assert billiejean_example.BILLIE_JEAN_YOUTUBE_URL == "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
    assert billiejean_example.LLM_BASE_URL == "https://api.llm7.io/v1"
    assert billiejean_example.LLM_MODEL == "gpt-4o-mini"
    assert billiejean_example.LLM_API_KEY == "unused"
    assert billiejean_example.OUTPUT_PATH.name == "billiejean_example.json"
