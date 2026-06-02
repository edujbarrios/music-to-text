import json
from pathlib import Path


def test_billiejean_example_json_is_valid() -> None:
    example_path = Path("examples/billiejean_example.json")

    payload = json.loads(example_path.read_text(encoding="utf-8"))

    assert payload["example_name"] == "billiejean_llm7io_youtube_demo"
    assert payload["source"]["url"] == "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
    assert payload["llm_provider_example"]["base_url"] == "https://api.llm7.io/v1"
    assert "with_llm" in payload["command"]
