from typer.testing import CliRunner

from music_to_text import __version__
from music_to_text.cli import app


def test_cli_version_option() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == f"music-to-text {__version__}"
