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
    assert billiejean_example.BILLIE_JEAN_AUDIO_PATH_ENV == "BILLIE_JEAN_AUDIO_PATH"
    assert billiejean_example.OUTPUT_PATH.name == "billiejean_example.json"


def test_billiejean_example_defaults_to_common_browser_cookies(monkeypatch) -> None:
    monkeypatch.delenv("YTDLP_COOKIES_FROM_BROWSER", raising=False)

    assert billiejean_example._browser_cookie_sources() == ("chrome", "edge", "firefox")


def test_billiejean_example_accepts_configured_browser_cookies(monkeypatch) -> None:
    monkeypatch.setenv("YTDLP_COOKIES_FROM_BROWSER", "chrome:Profile 1")

    assert billiejean_example._browser_cookie_sources() == ("chrome:Profile 1",)


def test_billiejean_example_help_message_mentions_local_audio_fallback() -> None:
    message = billiejean_example._download_help_message()

    assert "YTDLP_COOKIES" in message
    assert "BILLIE_JEAN_AUDIO_PATH" in message
    assert "python -m pip install -U yt-dlp" in message


def test_billiejean_example_main_prints_clean_error(monkeypatch, capsys) -> None:
    monkeypatch.setattr(billiejean_example, "run", lambda: (_ for _ in ()).throw(RuntimeError("clean help")))

    exit_code = billiejean_example.main()

    assert exit_code == 1
    assert capsys.readouterr().out == "clean help\n"
