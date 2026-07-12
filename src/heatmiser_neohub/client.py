"""Async WebSocket client for the IMI Heatmiser NeoHub API (port 4243)."""

from __future__ import annotations

import asyncio
import json
import os
import ssl
from typing import Any

from websockets.asyncio.client import ClientConnection, connect

from heatmiser_neohub.models import LiveData, SystemInfo
from heatmiser_neohub.protocol import build_request, parse_response


class NeoHubError(Exception):
    """Base error for NeoHub client failures."""


class NeoHubTimeoutError(NeoHubError):
    """Timed out waiting for a command response."""


class NeoHubClient:
    """Client for NeoHub WSS API on port 4243.

    The hub uses a locally generated TLS certificate, so certificate
    verification is disabled by default.
    """

    def __init__(
        self,
        host: str | None = None,
        token: str | None = None,
        port: int | None = None,
        *,
        verify_tls: bool = False,
        timeout: float = 15.0,
    ) -> None:
        self.host = host or os.environ.get("NEOHUB_HOST", "")
        self.token = token or os.environ.get("NEOHUB_TOKEN", "")
        from heatmiser_neohub.discover import resolve_hub_port

        self.port = resolve_hub_port(port)
        self.verify_tls = verify_tls
        self.timeout = timeout
        self._ws: ClientConnection | None = None
        self._command_id = 0
        self._lock = asyncio.Lock()

    @property
    def uri(self) -> str:
        return f"wss://{self.host}:{self.port}"

    def _ssl_context(self) -> ssl.SSLContext | bool:
        if self.verify_tls:
            return True
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _require_config(self) -> None:
        if not self.host:
            from heatmiser_neohub.discover import DiscoveryError, resolve_hub_host

            try:
                self.host, _discovered = resolve_hub_host()
            except DiscoveryError as exc:
                raise NeoHubError(str(exc)) from exc
        if not self.token:
            raise NeoHubError(
                "NeoHub API token is required (pass token= or set NEOHUB_TOKEN)"
            )

    async def connect(self) -> None:
        """Open a persistent WSS connection to the hub."""
        self._require_config()
        if self._ws is not None:
            return
        self._ws = await connect(
            self.uri,
            ssl=self._ssl_context(),
            open_timeout=self.timeout,
            close_timeout=self.timeout,
        )

    async def close(self) -> None:
        """Close the WebSocket connection if open."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def __aenter__(self) -> NeoHubClient:
        await self.connect()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    def _next_command_id(self) -> int:
        self._command_id += 1
        return self._command_id

    async def command(self, cmd: dict[str, Any], *, command_id: int | None = None) -> Any:
        """Send a NeoHub JSON command and return the parsed ``response`` payload."""
        async with self._lock:
            if self._ws is None:
                await self.connect()
            assert self._ws is not None

            cid = command_id if command_id is not None else self._next_command_id()
            payload = build_request(self.token, cmd, command_id=cid)
            await self._ws.send(payload)

            deadline = asyncio.get_running_loop().time() + self.timeout
            while True:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    raise NeoHubTimeoutError(
                        f"Timed out waiting for response to command_id={cid}"
                    )
                try:
                    raw = await asyncio.wait_for(self._ws.recv(), timeout=remaining)
                except TimeoutError as exc:
                    raise NeoHubTimeoutError(
                        f"Timed out waiting for response to command_id={cid}"
                    ) from exc

                parsed = parse_response(raw)
                if parsed.get("command_id") == cid:
                    return parsed["response"]
                # Ignore unrelated frames and keep waiting for our command_id

    async def get_live_data(self) -> LiveData:
        response = await self.command({"GET_LIVE_DATA": 0})
        if not isinstance(response, dict):
            raise NeoHubError(f"Unexpected GET_LIVE_DATA response: {response!r}")
        return LiveData.from_dict(response)

    async def get_system(self) -> SystemInfo:
        response = await self.command({"GET_SYSTEM": 0})
        if not isinstance(response, dict):
            raise NeoHubError(f"Unexpected GET_SYSTEM response: {response!r}")
        return SystemInfo.from_dict(response)

    async def get_firmware(self) -> Any:
        return await self.command({"FIRMWARE": 0})

    def run(self, coro: Any) -> Any:
        """Run an async coroutine against this client (CLI convenience)."""
        return asyncio.run(coro)


def dumps_pretty(obj: Any) -> str:
    """Pretty-print a model or dict as JSON."""
    data = obj.raw if hasattr(obj, "raw") and isinstance(obj.raw, dict) else obj
    if not isinstance(data, (dict, list)):
        data = json.loads(json.dumps(data, default=str))
    return json.dumps(data, indent=2, sort_keys=True)
