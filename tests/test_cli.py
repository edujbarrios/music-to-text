from typer.testing import CliRunner

from music_to_text import __version__
from music_to_text.cli import _write_or_print, app


def test_cli_creates_output_parent_directories(monkeypatch, tmp_path) -> None:
    output = tmp_path / "reports" / "nested" / "analysis.json"
    monkeypatch.setattr("music_to_text.cli.format_result", lambda *args, **kwargs: "result")

    _write_or_print(object(), mode="summary", output=output, pretty=False, output_format="text")

    assert output.read_text(encoding="utf-8") == "result"


def test_cli_version_option() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == f"music-to-text {__version__}"


def test_cli_list_files_option(tmp_path) -> None:
    (tmp_path / "b.mp3").write_bytes(b"fake")
    (tmp_path / "a.wav").write_bytes(b"fake")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")

    result = CliRunner().invoke(app, [str(tmp_path), "--list-files"])

    assert result.exit_code == 0
    assert result.output.splitlines() == [
        str(tmp_path / "a.wav"),
        str(tmp_path / "b.mp3"),
    ]


def test_cli_list_files_respects_limit(tmp_path) -> None:
    (tmp_path / "a.wav").write_bytes(b"fake")
    (tmp_path / "b.mp3").write_bytes(b"fake")

    result = CliRunner().invoke(app, [str(tmp_path), "--list-files", "--limit", "1"])

    assert result.exit_code == 0
    assert result.output.splitlines() == [str(tmp_path / "a.wav")]
