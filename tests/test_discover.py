"""Tests for hub host resolution / discovery helpers."""

from __future__ import annotations

import json

import pytest

from heatmiser_neohub.discover import (
    DiscoveredHub,
    DiscoveryError,
    discover_hubs,
    resolve_hub_host,
    resolve_hub_port,
)


def test_resolve_hub_host_uses_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NEOHUB_HOST", raising=False)
    host, discovered = resolve_hub_host("192.168.0.19")
    assert host == "192.168.0.19"
    assert discovered is False


def test_resolve_hub_host_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEOHUB_HOST", "10.0.0.5")
    host, discovered = resolve_hub_host(None)
    assert host == "10.0.0.5"
    assert discovered is False


def test_resolve_hub_host_discovers_single(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NEOHUB_HOST", raising=False)

    def fake_discover(**_: object) -> list[DiscoveredHub]:
        return [DiscoveredHub(ip="192.168.1.10", device_id="AA:BB")]

    monkeypatch.setattr(
        "heatmiser_neohub.discover.discover_hubs", fake_discover
    )
    host, discovered = resolve_hub_host(None)
    assert host == "192.168.1.10"
    assert discovered is True


def test_resolve_hub_host_errors_when_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NEOHUB_HOST", raising=False)
    monkeypatch.setattr(
        "heatmiser_neohub.discover.discover_hubs", lambda **_: []
    )
    with pytest.raises(DiscoveryError, match="found no hubs"):
        resolve_hub_host(None)


def test_resolve_hub_host_errors_when_multiple(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NEOHUB_HOST", raising=False)

    def fake_discover(**_: object) -> list[DiscoveredHub]:
        return [
            DiscoveredHub(ip="192.168.1.10"),
            DiscoveredHub(ip="192.168.1.11", device_id="CC:DD"),
        ]

    monkeypatch.setattr(
        "heatmiser_neohub.discover.discover_hubs", fake_discover
    )
    with pytest.raises(DiscoveryError, match="Multiple NeoHubs"):
        resolve_hub_host(None)


def test_resolve_hub_port_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NEOHUB_PORT", raising=False)
    assert resolve_hub_port(None) == 4243


def test_resolve_hub_port_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEOHUB_PORT", "9999")
    assert resolve_hub_port(4243) == 4243


def test_resolve_hub_port_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEOHUB_PORT", "4243")
    assert resolve_hub_port(None) == 4243


def test_discover_hubs_parses_udp_replies(monkeypatch: pytest.MonkeyPatch) -> None:
    replies = [
        (
            json.dumps({"ip": "192.168.1.20", "device_id": "AA"}).encode(),
            ("192.168.1.20", 19790),
        ),
        (b"not-json", ("192.168.1.21", 19790)),
    ]

    class FakeSock:
        def __init__(self, *_a: object, **_k: object) -> None:
            self._replies = list(replies)

        def setsockopt(self, *_a: object, **_k: object) -> None:
            return None

        def settimeout(self, *_a: object, **_k: object) -> None:
            return None

        def bind(self, *_a: object, **_k: object) -> None:
            return None

        def sendto(self, *_a: object, **_k: object) -> None:
            return None

        def recvfrom(self, *_a: object, **_k: object):
            if not self._replies:
                raise TimeoutError
            return self._replies.pop(0)

        def close(self) -> None:
            return None

    monkeypatch.setattr("heatmiser_neohub.discover.socket.socket", FakeSock)
    hubs = discover_hubs(timeout=0.1)
    by_ip = {h.ip: h for h in hubs}
    assert by_ip["192.168.1.20"].device_id == "AA"
    assert "192.168.1.21" in by_ip
