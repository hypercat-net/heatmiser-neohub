"""Unit tests for NeoHubClient with a fake WebSocket."""

from __future__ import annotations

import json
from typing import Any

import pytest

from heatmiser_neohub.client import (
    NeoHubClient,
    NeoHubError,
    NeoHubTimeoutError,
    _redact_token,
    dumps_pretty,
)
from heatmiser_neohub.models import LiveData
from heatmiser_neohub.protocol import build_request


class FakeWS:
    def __init__(self, responses: list[str | bytes]) -> None:
        self._responses = list(responses)
        self.sent: list[str] = []
        self.closed = False

    async def send(self, data: str) -> None:
        self.sent.append(data)

    async def recv(self) -> str | bytes:
        if not self._responses:
            raise TimeoutError("no more fake responses")
        return self._responses.pop(0)

    async def close(self) -> None:
        self.closed = True


def _hub_response(command_id: int, payload: dict[str, Any]) -> str:
    return json.dumps(
        {
            "command_id": command_id,
            "message_type": "hm_set_command_response",
            "response": json.dumps(payload),
        }
    )


@pytest.mark.asyncio
async def test_command_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeWS([_hub_response(1, {"HUB_TIME": 123})])

    async def fake_connect(*_a: object, **_k: object) -> FakeWS:
        return fake

    monkeypatch.setattr("heatmiser_neohub.client.connect", fake_connect)

    client = NeoHubClient(host="192.168.0.1", token="secret", timeout=2.0)
    async with client:
        result = await client.command({"GET_LIVE_DATA": 0})

    assert result == {"HUB_TIME": 123}
    assert fake.closed is True
    assert len(fake.sent) == 1
    outer = json.loads(fake.sent[0])
    inner = json.loads(outer["message"])
    assert inner["token"] == "secret"
    assert inner["COMMANDS"][0]["COMMAND"] == "{'GET_LIVE_DATA': 0}"


@pytest.mark.asyncio
async def test_command_ignores_unrelated_frames(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = FakeWS(
        [
            _hub_response(99, {"noise": True}),
            _hub_response(1, {"ok": True}),
        ]
    )

    async def fake_connect(*_a: object, **_k: object) -> FakeWS:
        return fake

    monkeypatch.setattr("heatmiser_neohub.client.connect", fake_connect)

    client = NeoHubClient(host="192.168.0.1", token="t", timeout=2.0)
    await client.connect()
    result = await client.command({"FIRMWARE": 0})
    assert result == {"ok": True}
    await client.close()


@pytest.mark.asyncio
async def test_command_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeWS([])  # recv always times out

    async def fake_connect(*_a: object, **_k: object) -> FakeWS:
        return fake

    monkeypatch.setattr("heatmiser_neohub.client.connect", fake_connect)

    client = NeoHubClient(host="192.168.0.1", token="t", timeout=0.05)
    await client.connect()
    with pytest.raises(NeoHubTimeoutError):
        await client.command({"FIRMWARE": 0})
    await client.close()


@pytest.mark.asyncio
async def test_get_live_data_and_system(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = [
        _hub_response(1, {"HUB_TIME": 1, "devices": []}),
        _hub_response(2, {"DEVICE_ID": "hub", "HUB_VERSION": 2410}),
        _hub_response(3, {"firmware version": "2153"}),
    ]
    fake = FakeWS(responses)

    async def fake_connect(*_a: object, **_k: object) -> FakeWS:
        return fake

    monkeypatch.setattr("heatmiser_neohub.client.connect", fake_connect)

    client = NeoHubClient(host="192.168.0.1", token="t")
    await client.connect()
    live = await client.get_live_data()
    assert isinstance(live, LiveData)
    assert live.hub_time == 1
    system = await client.get_system()
    assert system.device_id == "hub"
    assert await client.get_firmware() == {"firmware version": "2153"}
    await client.close()


@pytest.mark.asyncio
async def test_get_live_data_rejects_non_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = FakeWS(
        [
            json.dumps(
                {
                    "command_id": 1,
                    "response": json.dumps("nope"),
                }
            )
        ]
    )

    async def fake_connect(*_a: object, **_k: object) -> FakeWS:
        return fake

    monkeypatch.setattr("heatmiser_neohub.client.connect", fake_connect)

    client = NeoHubClient(host="192.168.0.1", token="t")
    await client.connect()
    with pytest.raises(NeoHubError, match="Unexpected GET_LIVE_DATA"):
        await client.get_live_data()
    await client.close()


def test_require_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NEOHUB_TOKEN", raising=False)
    client = NeoHubClient(host="192.168.0.1", token=None)
    with pytest.raises(NeoHubError, match="token"):
        client._require_config()


def test_require_host_discovers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NEOHUB_HOST", raising=False)

    def fake_resolve(host: str | None = None, **_: object) -> tuple[str, bool]:
        return "10.0.0.2", True

    monkeypatch.setattr(
        "heatmiser_neohub.discover.resolve_hub_host", fake_resolve
    )
    client = NeoHubClient(host="", token="t")
    client._require_config()
    assert client.host == "10.0.0.2"


def test_ssl_context_verify_modes() -> None:
    client = NeoHubClient(host="h", token="t", verify_tls=False)
    ctx = client._ssl_context()
    assert ctx is not True
    assert client.uri == "wss://h:4243"

    verified = NeoHubClient(host="h", token="t", verify_tls=True)
    assert verified._ssl_context() is True


def test_redact_and_dumps_pretty() -> None:
    payload = build_request("secret-token", {"GET_SYSTEM": 0})
    assert "secret-token" not in _redact_token(payload, "secret-token")
    assert _redact_token("x", "") == "x"

    live = LiveData.from_dict({"HUB_TIME": 9, "devices": []})
    text = dumps_pretty(live)
    assert '"HUB_TIME": 9' in text
    assert dumps_pretty({"a": 1}).startswith("{")
