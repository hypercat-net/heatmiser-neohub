"""CLI smoke tests for global options and commands."""

from __future__ import annotations

import re
from typing import Any

import pytest
from typer.testing import CliRunner

from heatmiser_neohub import __version__
from heatmiser_neohub.cli import app
from heatmiser_neohub.client import NeoHubError
from heatmiser_neohub.discover import DiscoveredHub
from heatmiser_neohub.models import LiveData, SystemInfo

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


def test_verbose_enables_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_basicConfig(**kwargs: Any) -> None:
        calls.append(kwargs)

    monkeypatch.setattr("heatmiser_neohub.cli.logging.basicConfig", fake_basicConfig)
    monkeypatch.setattr("heatmiser_neohub.cli.discover_hubs", lambda **_: [])
    result = runner.invoke(app, ["--verbose", "discover"])
    assert result.exit_code == 1
    assert calls
    assert calls[0]["level"] == 20  # logging.INFO


def test_discover_lists_hubs(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_discover(**kwargs: Any) -> list[DiscoveredHub]:
        calls.append(kwargs)
        return [DiscoveredHub(ip="10.0.0.1", device_id="AA")]

    monkeypatch.setattr(
        "heatmiser_neohub.cli.discover_hubs",
        fake_discover,
    )
    result = runner.invoke(
        app, ["discover", "--bind-address", "192.168.1.20"]
    )
    assert result.exit_code == 0
    assert "10.0.0.1" in result.stdout
    assert "AA" in result.stdout
    assert calls[0]["bind_address"] == "192.168.1.20"


def test_discover_bind_address_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_discover(**kwargs: Any) -> list[DiscoveredHub]:
        calls.append(kwargs)
        return [DiscoveredHub(ip="10.0.0.1")]

    monkeypatch.setattr("heatmiser_neohub.cli.discover_hubs", fake_discover)
    result = runner.invoke(
        app, ["discover"], env={"NEOHUB_BIND_ADDRESS": "192.168.1.21"}
    )
    assert result.exit_code == 0
    assert calls[0]["bind_address"] == "192.168.1.21"


def test_discover_none_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("heatmiser_neohub.cli.discover_hubs", lambda **_: [])
    result = runner.invoke(app, ["discover"])
    assert result.exit_code == 1


def test_live_data_command(monkeypatch: pytest.MonkeyPatch) -> None:
    resolved_bind_addresses: list[str] = []

    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_exc: object) -> None:
            return None

        async def get_live_data(self) -> LiveData:
            return LiveData.from_dict({"HUB_TIME": 42, "devices": []})

    def fake_resolve_hub_host(
        host: str | None, *, bind_address: str
    ) -> tuple[str, bool]:
        assert host is None
        resolved_bind_addresses.append(bind_address)
        return "10.0.0.1", False

    monkeypatch.setattr(
        "heatmiser_neohub.cli.resolve_hub_host", fake_resolve_hub_host
    )
    monkeypatch.setattr("heatmiser_neohub.cli.NeoHubClient", FakeClient)
    result = runner.invoke(
        app,
        [
            "live-data",
            "--token",
            "t",
            "--bind-address",
            "192.168.1.20",
        ],
    )
    assert result.exit_code == 0
    assert "HUB_TIME" in result.stdout
    assert resolved_bind_addresses == ["192.168.1.20"]


def test_system_and_cmd(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_exc: object) -> None:
            return None

        async def get_system(self) -> SystemInfo:
            return SystemInfo.from_dict({"DEVICE_ID": "hub"})

        async def command(self, payload: dict[str, Any]) -> dict[str, Any]:
            return {"echo": payload}

    monkeypatch.setattr(
        "heatmiser_neohub.cli.resolve_hub_host",
        lambda host, **_: ("10.0.0.1", False),
    )
    monkeypatch.setattr("heatmiser_neohub.cli.NeoHubClient", FakeClient)

    system = runner.invoke(app, ["system", "--host", "10.0.0.1", "--token", "t"])
    assert system.exit_code == 0
    assert "hub" in system.stdout

    cmd = runner.invoke(
        app, ["cmd", '{"FIRMWARE":0}', "--host", "10.0.0.1", "--token", "t"]
    )
    assert cmd.exit_code == 0
    assert "FIRMWARE" in cmd.stdout

    bad = runner.invoke(app, ["cmd", "not-json", "--host", "10.0.0.1", "--token", "t"])
    assert bad.exit_code == 1


def test_live_data_neohub_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_exc: object) -> None:
            return None

        async def get_live_data(self) -> LiveData:
            raise NeoHubError("boom")

    monkeypatch.setattr(
        "heatmiser_neohub.cli.resolve_hub_host",
        lambda host, **_: ("10.0.0.1", False),
    )
    monkeypatch.setattr("heatmiser_neohub.cli.NeoHubClient", FakeClient)
    result = runner.invoke(
        app, ["live-data", "--host", "10.0.0.1", "--token", "t"]
    )
    assert result.exit_code == 1
    assert "boom" in result.stderr
