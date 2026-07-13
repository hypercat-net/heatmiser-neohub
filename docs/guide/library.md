# Python client library

Import from `heatmiser_neohub`. The client speaks the modern NeoHub **WSS** API on
port **4243** (TLS certificate verification disabled by default — the hub uses a
locally generated cert).

## Stability (1.0)

Public symbols are those exported from `heatmiser_neohub` (see `__all__`): the
client, models, discovery helpers, and errors. The library is a thin protocol
client — it does not wrap every NeoHub command, auto-reconnect dropped sockets,
or raise on hub `{"error": …}` response payloads (those are returned as data).

## Install

From [PyPI](https://pypi.org/project/heatmiser-neohub/):

```bash
pip install heatmiser-neohub
```

## Quick example

```python
import asyncio
from heatmiser_neohub import NeoHubClient

async def main() -> None:
    async with NeoHubClient(host="192.168.0.19", token="YOUR_TOKEN") as client:
        live = await client.get_live_data()
        for device in live.devices:
            print(device.zone_name, device.actual_temp, device.set_temp)

asyncio.run(main())
```

`host` / `token` / `port` can also come from `NEOHUB_HOST`, `NEOHUB_TOKEN`, and
`NEOHUB_PORT`. If `host` is omitted, the client auto-discovers when exactly one
hub is on the LAN (same rules as the CLI).

## Main API

### `NeoHubClient`

| Method | Description |
| --- | --- |
| `await connect()` / `await close()` | Manage the persistent WebSocket |
| `async with NeoHubClient(...)` | Context manager around connect/close |
| `await command({...})` | Send any NeoHub JSON command; returns parsed `response` |
| `await get_live_data()` | `GET_LIVE_DATA` → `LiveData` |
| `await get_system()` | `GET_SYSTEM` → `SystemInfo` |
| `await get_firmware()` | `FIRMWARE` |

### Models

- **`LiveData`** — hub timestamps, away/holiday flags, and `devices: list[Device]`
- **`Device`** — zone name, temps, heat/cool/standby/offline flags, profile ids, etc.
  - **`available_modes`** — lowercased `AVAILABLE_MODES` from the hub (`["heat"]`,
    `["heat", "cool"]`, …), or `None` when the field is absent
  - **`supports_mode(mode)`** — `True` if that mode is advertised; when
    `available_modes` is `None`, returns `True` (unknown → treat as supported)
  - Also maps humidity, preheat, modulation, hold/level, lock, floor limit, and
    HC/fan string fields from live data
- **`SystemInfo`** — hub version, `HUB_TYPE`, format, timezone, NTP/DST fields

Raw hub payloads remain available on each model as `.raw`.

### Discovery helpers

```python
from heatmiser_neohub.discover import discover_hubs, resolve_hub_host

for hub in discover_hubs(timeout=2.0):
    print(hub.ip, hub.device_id)

host, discovered = resolve_hub_host()  # raises DiscoveryError if 0 or 2+ hubs
```

## Errors

- `NeoHubError` — configuration or protocol failures
- `NeoHubTimeoutError` — no matching `command_id` response within the timeout
- `DiscoveryError` — auto-discover found no hub or multiple hubs

## Protocol notes

Commands are wrapped in the authenticated WSS envelope described in the
[NeoHub API guide](api/neohub-api.html). For an interactive command catalogue,
see the secondary [OpenAPI / Swagger](swagger/) page.

### `COMMAND` field encoding

The outer frame and nested `message` string are standard
[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) JSON (double-quoted strings).
The hub's `COMMAND` value is **not**: Heatmiser requires a single-quoted
pseudo-JSON object such as `{'GET_LIVE_DATA': 0}` (see the
[API reference](api/neohub-api.html#command-quoting-vs-standard-json)).

RFC 8259 §7 defines JSON strings with U+0022 quotation marks; a standard
encoding like `{"GET_LIVE_DATA":0}` is valid JSON but the NeoHub rejects it
inside `COMMAND` with `Invalid Json`. This library uses Python `str(dict)` so
callers can pass normal dicts to `command()` / `get_live_data()` and still get
the Heatmiser wire form.
