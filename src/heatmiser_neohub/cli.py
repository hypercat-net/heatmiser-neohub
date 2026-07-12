"""Typer CLI for the IMI Heatmiser NeoHub API.

Connection settings can be supplied via flags or environment variables:

    NEOHUB_HOST   hostname or IP (optional — auto-discovers if exactly one hub)
    NEOHUB_TOKEN  API token configured on the hub
    NEOHUB_PORT   WSS port (default 4243)
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Awaitable, Optional

import typer
from dotenv import load_dotenv

from heatmiser_neohub.client import NeoHubClient, NeoHubError, dumps_pretty
from heatmiser_neohub.discover import DiscoveryError, discover_hubs, resolve_hub_host, resolve_hub_port

# Load .env from the current working directory (does not override real env).
load_dotenv()

app = typer.Typer(
    help="Command line interface for the IMI Heatmiser NeoHub API.",
    no_args_is_help=True,
)

HostOption = typer.Option(
    None,
    "--host",
    envvar="NEOHUB_HOST",
    help="NeoHub hostname or IP. If omitted, auto-discovers when exactly one hub is on the LAN.",
)
TokenOption = typer.Option(
    None, "--token", envvar="NEOHUB_TOKEN", help="NeoHub API token."
)
PortOption = typer.Option(
    None,
    "--port",
    envvar="NEOHUB_PORT",
    help="NeoHub WSS port. Defaults to 4243 when omitted.",
)


def _make_client(
    host: Optional[str], token: Optional[str], port: Optional[int]
) -> NeoHubClient:
    try:
        resolved, discovered = resolve_hub_host(host)
    except DiscoveryError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    if discovered:
        typer.secho(f"Discovered NeoHub at {resolved}", fg=typer.colors.CYAN, err=True)
    resolved_port = resolve_hub_port(port)
    return NeoHubClient(host=resolved, token=token, port=resolved_port)


def _run(coro: Awaitable[Any]) -> Any:
    """Run an async coroutine, converting NeoHub errors into CLI exits."""
    try:
        return asyncio.run(coro)
    except NeoHubError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def discover(
    timeout: float = typer.Option(
        2.0, "--timeout", help="Seconds to wait for hub replies."
    ),
    broadcast: str = typer.Option(
        "255.255.255.255", "--broadcast", help="Broadcast address to send hubseek to."
    ),
) -> None:
    """Discover NeoHubs on the local network via UDP broadcast (hubseek)."""
    hubs = discover_hubs(timeout=timeout, broadcast_address=broadcast)
    if not hubs:
        typer.echo("No NeoHubs found.")
        raise typer.Exit(code=1)
    for hub in hubs:
        typer.echo(f"{hub.ip}\tdevice_id={hub.device_id}")


@app.command("live-data")
def live_data(
    host: Optional[str] = HostOption,
    token: Optional[str] = TokenOption,
    port: int = PortOption,
) -> None:
    """Fetch and print GET_LIVE_DATA from the hub as JSON."""
    client = _make_client(host, token, port)

    async def _fetch() -> str:
        async with client:
            data = await client.get_live_data()
        return dumps_pretty(data)

    typer.echo(_run(_fetch()))


@app.command()
def system(
    host: Optional[str] = HostOption,
    token: Optional[str] = TokenOption,
    port: int = PortOption,
) -> None:
    """Fetch and print GET_SYSTEM from the hub as JSON."""
    client = _make_client(host, token, port)

    async def _fetch() -> str:
        async with client:
            data = await client.get_system()
        return dumps_pretty(data)

    typer.echo(_run(_fetch()))


@app.command()
def cmd(
    command: str = typer.Argument(
        ..., help='JSON command object to send, e.g. \'{"GET_SYSTEM":0}\''
    ),
    host: Optional[str] = HostOption,
    token: Optional[str] = TokenOption,
    port: int = PortOption,
) -> None:
    """Send an arbitrary JSON command to the hub and print the raw response."""
    try:
        payload = json.loads(command)
    except json.JSONDecodeError as exc:
        typer.secho(f"Invalid JSON command: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    client = _make_client(host, token, port)

    async def _send() -> str:
        async with client:
            response = await client.command(payload)
        return json.dumps(response, indent=2, sort_keys=True)

    typer.echo(_run(_send()))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
