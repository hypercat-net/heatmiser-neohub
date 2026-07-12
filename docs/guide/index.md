# heatmiser-neohub

Python **client library** and **`neohub` CLI** for the IMI Heatmiser NeoHub
WebSocket API (port `4243`), with LAN discovery via UDP `hubseek` (port `19790`).

## Guides

- [CLI (`neohub`)](cli.html) — install, configuration, commands, Docker tips
- [Python library](library.html) — `NeoHubClient`, models, discovery helpers

## Quick start

```bash
pip install heatmiser-neohub
cp .env.example .env   # set NEOHUB_TOKEN (host optional if one hub on LAN)
neohub discover
neohub live-data
```

```python
import asyncio
from heatmiser_neohub import NeoHubClient

async def main() -> None:
    async with NeoHubClient(token="YOUR_TOKEN") as client:  # host auto-discovered
        live = await client.get_live_data()
        print(live.devices[0].zone_name, live.devices[0].actual_temp)

asyncio.run(main())
```

## Reference (secondary)

These pages document the underlying NeoHub protocol. Most application code only
needs the CLI or `NeoHubClient`.

- [NeoHub API guide](api/neohub-api.html) — protocol notes (from official docs)
- [OpenAPI / Swagger](swagger/) — interactive command catalogue
- [openapi.yaml](openapi/neohub-api.openapi.yaml) — machine-readable spec
- [Official NeoHub API PDF](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf) — IMI Heatmiser source

## Links

- [GitHub repository](https://github.com/hypercat-net/heatmiser-neohub)
- [Docker Hub](https://hub.docker.com/r/hypercat/heatmiser-neohub)
- [neoHub product page](https://www.heatmiser.com/neohub-smart-control/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)
