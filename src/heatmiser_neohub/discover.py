"""UDP discovery for NeoHub devices (hubseek)."""

from __future__ import annotations

import json
import os
import socket
from dataclasses import dataclass


HUBSEEK_PORT = 19790
HUBSEEK_PAYLOAD = b"hubseek"


class DiscoveryError(Exception):
    """Raised when hub discovery fails or is ambiguous."""


@dataclass(slots=True)
class DiscoveredHub:
    ip: str
    device_id: str | None = None
    raw: dict | None = None


def discover_hubs(
    timeout: float = 2.0,
    broadcast_address: str = "255.255.255.255",
    port: int = HUBSEEK_PORT,
) -> list[DiscoveredHub]:
    """Broadcast ``hubseek`` and collect NeoHub replies.

    NeoHubs respond with JSON like ``{"ip":"192.168.0.19","device_id":"…"}``.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    hubs: dict[str, DiscoveredHub] = {}
    try:
        sock.bind(("", 0))
        sock.sendto(HUBSEEK_PAYLOAD, (broadcast_address, port))

        while True:
            try:
                data, addr = sock.recvfrom(4096)
            except TimeoutError:
                break

            text = data.decode("utf-8", errors="replace").strip()
            ip = addr[0]
            device_id = None
            raw: dict | None = None
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    raw = parsed
                    ip = str(parsed.get("ip") or ip)
                    device_id = parsed.get("device_id")
            except json.JSONDecodeError:
                pass

            hubs[ip] = DiscoveredHub(ip=ip, device_id=device_id, raw=raw)
    finally:
        sock.close()

    return list(hubs.values())


def resolve_hub_host(
    host: str | None = None,
    *,
    timeout: float = 2.0,
    broadcast_address: str = "255.255.255.255",
) -> tuple[str, bool]:
    """Resolve a NeoHub host, discovering on the LAN if needed.

    Returns ``(host, discovered)`` where ``discovered`` is True when the host
    was found via UDP hubseek rather than supplied explicitly / via env.

    Raises:
        DiscoveryError: if no hub is found, or more than one hub responds.
    """
    explicit = (host or os.environ.get("NEOHUB_HOST") or "").strip()
    if explicit:
        return explicit, False

    hubs = discover_hubs(timeout=timeout, broadcast_address=broadcast_address)
    if not hubs:
        raise DiscoveryError(
            "NeoHub host is not set and discovery found no hubs "
            "(set NEOHUB_HOST / --host, or run `neohub discover`)"
        )
    if len(hubs) > 1:
        found = ", ".join(
            f"{h.ip}" + (f" ({h.device_id})" if h.device_id else "") for h in hubs
        )
        raise DiscoveryError(
            f"Multiple NeoHubs found ({found}); set NEOHUB_HOST or --host to choose one"
        )
    return hubs[0].ip, True


DEFAULT_WSS_PORT = 4243


def resolve_hub_port(port: int | None = None) -> int:
    """Resolve the NeoHub WSS port.

    Uses ``port`` if given, else ``NEOHUB_PORT``, else the modern default
    ``4243``. UDP hubseek does not advertise a port.
    """
    if port is not None:
        return int(port)
    env = (os.environ.get("NEOHUB_PORT") or "").strip()
    if env:
        return int(env)
    return DEFAULT_WSS_PORT
