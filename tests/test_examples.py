import json
from pathlib import Path

from examples import billiejean_example


def test_billiejean_example_json_is_valid() -> None:
    example_path = Path("examples/billiejean_example.json")

    payload = json.loads(example_path.read_text(encoding="utf-8"))

    assert payload["source_path"] == "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
    assert payload["mode"] == "json"
    assert "features" in payload
    assert "generated_text" in payload
    assert payload["extra"]["source_metadata"]["title"] == "Michael Jackson - Billie Jean (Official Video)"


def test_billiejean_example_script_configuration() -> None:
    assert billiejean_example.BILLIE_JEAN_YOUTUBE_URL == "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"
    assert billiejean_example.LLM_BASE_URL == "https://api.llm7.io/v1"
    assert billiejean_example.LLM_MODEL
    assert billiejean_example.LLM_API_KEY
    assert billiejean_example.BILLIE_JEAN_AUDIO_PATH_ENV == "BILLIE_JEAN_AUDIO_PATH"
    assert billiejean_example.OUTPUT_PATH.name == "billiejean_example.json"
    assert billiejean_example.DOWNLOAD_DIR.name == "_downloads"


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


def test_billiejean_example_llm_fallback_records_error() -> None:
    class FakeAnalyzer:
        def analyze(self, source, mode="json", download_dir=None, cookies=None, cookies_from_browser=None, llm_fallback=False):
            class FakeResult:
                extra = {
                    "llm_error": "402 Client Error: Payment Required",
                    "llm_fallback_used": True,
                }

            assert llm_fallback is True
            assert download_dir == billiejean_example.DOWNLOAD_DIR
            return FakeResult()

    result = billiejean_example._analyze_with_llm_fallback(FakeAnalyzer(), "song.mp3")

    assert result.extra["llm_fallback_used"] is True
    assert "Payment Required" in result.extra["llm_error"]
    assert result.extra["llm_provider_example"]["api_key_env_var"] == "LLM_API_KEY"
    assert result.extra["llm_provider_example"]["api_key_configured"] is True


def test_billiejean_example_main_prints_clean_error(monkeypatch, capsys) -> None:
    monkeypatch.setattr(billiejean_example, "run", lambda: (_ for _ in ()).throw(RuntimeError("clean help")))

    exit_code = billiejean_example.main()

    assert exit_code == 1
    assert capsys.readouterr().out == "clean help\n"
