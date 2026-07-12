# Python client library

Import from `heatmiser_neohub`. The client speaks the modern NeoHub **WSS** API on
port **4243** (TLS certificate verification disabled by default — the hub uses a
locally generated cert).

## Install

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
