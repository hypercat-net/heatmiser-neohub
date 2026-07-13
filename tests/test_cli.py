"""CLI smoke tests for global options."""

from __future__ import annotations

import re

from typer.testing import CliRunner

from heatmiser_neohub import __version__
from heatmiser_neohub.cli import app

runner = CliRunner()

# Rich may colour help even when CliRunner passes color=False (e.g. in CI),
# splitting "--version" into "-\x1b…-version" and breaking substring checks.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    return _ANSI_RE.sub("", text)


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_version_short_flag() -> None:
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_help_lists_global_options() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    help_text = _plain(result.stdout)
    assert "--version" in help_text
    assert "--verbose" in help_text
    assert "--debug" in help_text
