"""CLI smoke tests for global options."""

from __future__ import annotations

from typer.testing import CliRunner

from heatmiser_neohub import __version__
from heatmiser_neohub.cli import app

runner = CliRunner()


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
    assert "--version" in result.stdout
    assert "--verbose" in result.stdout
    assert "--debug" in result.stdout
