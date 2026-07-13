# heatmiser-neohub

[![CI](https://github.com/hypercat-net/heatmiser-neohub/actions/workflows/tests.yaml/badge.svg)](https://github.com/hypercat-net/heatmiser-neohub/actions/workflows/tests.yaml) [![Pages](https://github.com/hypercat-net/heatmiser-neohub/actions/workflows/pages.yaml/badge.svg)](https://github.com/hypercat-net/heatmiser-neohub/actions/workflows/pages.yaml) [![PyPI](https://img.shields.io/pypi/v/heatmiser-neohub)](https://pypi.org/project/heatmiser-neohub/) [![License](https://img.shields.io/github/license/hypercat-net/heatmiser-neohub)](https://github.com/hypercat-net/heatmiser-neohub/blob/main/LICENSE) [![Docker](https://img.shields.io/docker/v/hypercat42/heatmiser-neohub?label=docker)](https://hub.docker.com/r/hypercat42/heatmiser-neohub)

Python client library and command-line interface for the IMI Heatmiser NeoHub API
(WebSocket/WSS control interface on port 4243, plus UDP `hubseek` discovery on
port 19790).

[![BuyMeACoffee](https://raw.githubusercontent.com/barcar/buymeacoffee-badges/main/bmc-donate-white.svg)](https://buymeacoffee.com/barcar)

See `docs/reference/neohub-api-rev-3.02.md` for the full protocol reference this
library implements.

## Related links

- [PyPI](https://pypi.org/project/heatmiser-neohub/)
- [neoHub smart control (product)](https://www.heatmiser.com/neohub-smart-control/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)
- [Official NeoHub API PDF](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf)

## Documentation

Published docs (GitHub Pages):
[https://hypercat-net.github.io/heatmiser-neohub/](https://hypercat-net.github.io/heatmiser-neohub/)

- [CLI guide](https://hypercat-net.github.io/heatmiser-neohub/cli.html)
- [Python library guide](https://hypercat-net.github.io/heatmiser-neohub/library.html)
- [NeoHub API protocol guide](https://hypercat-net.github.io/heatmiser-neohub/api/neohub-api.html) (reference)
- [OpenAPI / Swagger](https://hypercat-net.github.io/heatmiser-neohub/swagger/) (secondary command catalogue)

Source markdown lives under [`docs/guide/`](docs/guide/) (product docs) and
[`docs/reference/neohub-api-rev-3.02.md`](docs/reference/neohub-api-rev-3.02.md) (protocol).

Build the site locally:

```bash
pip install "markdown>=3.10" "PyYAML>=6.0.3"
python scripts/build_docs_site.py -o site
open site/index.html
```

GitHub Pages is published by [`.github/workflows/pages.yaml`](.github/workflows/pages.yaml)
on pushes to `main`.

## Installation

Install from [PyPI](https://pypi.org/project/heatmiser-neohub/):

```bash
pip install heatmiser-neohub
```

For local development, install in editable mode with the `dev` extras:

```bash
pip install -e ".[dev]"
```

### Docker

A slim multi-arch image (`linux/amd64`, `linux/arm64`) is published to Docker Hub as
[`hypercat42/heatmiser-neohub`](https://hub.docker.com/r/hypercat42/heatmiser-neohub).
The image is built from this repository’s source (not installed from PyPI) so each
tag matches the git commit that produced it.

```bash
# Discovery uses UDP broadcast. Containers are isolated from the LAN by default,
# so on Linux use host networking for `discover` (and for auto-discover when
# NEOHUB_HOST is unset).
docker run --rm --network host hypercat42/heatmiser-neohub discover

docker run --rm -e NEOHUB_HOST -e NEOHUB_TOKEN hypercat42/heatmiser-neohub live-data
# or: docker run --rm --env-file .env hypercat42/heatmiser-neohub live-data
```

## Configuration

Copy [`.env.example`](.env.example) to `.env` and set your hub details:

```bash
cp .env.example .env
```

The `neohub` CLI loads `.env` automatically (real environment variables still win).
You can also pass flags or export variables yourself.

| Variable        | Flag       | Description                          | Default |
| ---------------- | ---------- | ------------------------------------- | ------- |
| `NEOHUB_HOST`     | `--host`   | Hostname or IP of the hub. If unset, auto-discovers when exactly one hub is on the LAN. | *(auto)* |
| `NEOHUB_TOKEN`    | `--token`  | API token configured on the hub       | *(required for hub commands)* |
| `NEOHUB_PORT`     | `--port`   | WSS port. If unset, defaults to 4243. | `4243`  |

```bash
# With .env in the working directory
neohub live-data

# Or export / Docker --env-file
export NEOHUB_HOST=192.168.0.19
export NEOHUB_TOKEN=your-api-token
docker run --rm --env-file .env hypercat42/heatmiser-neohub live-data
```

## CLI usage

The package installs a `neohub` console script:

```bash
# Discover NeoHubs on the local network
neohub discover

# Fetch live zone/device data
neohub live-data

# Fetch hub system settings
neohub system

# Send an arbitrary JSON command
neohub cmd '{"GET_SYSTEM":0}'

# Version / logging
neohub --version
neohub -v live-data
neohub --debug cmd '{"FIRMWARE":0}'
```

Global options: `--version`/`-V`, `--verbose`/`-v`, `--debug` (also
`NEOHUB_VERBOSE` / `NEOHUB_DEBUG`). Each command also accepts `--host`,
`--token`, and `--port`, which override the corresponding environment variables.

## Library example

```python
import asyncio

from heatmiser_neohub import NeoHubClient


async def main() -> None:
    async with NeoHubClient(host="192.168.0.19", token="your-api-token") as client:
        live_data = await client.get_live_data()
        for device in live_data.devices:
            print(device.zone_name, device.actual_temp, device.set_temp)


asyncio.run(main())
```

## Discovery

NeoHubs can be located on the local network without knowing their IP address:

```python
from heatmiser_neohub.discover import discover_hubs

for hub in discover_hubs():
    print(hub.ip, hub.device_id)
```

## Development

```bash
pip install -e ".[dev]"
pytest   # includes coverage; fail_under is configured in pyproject.toml
```

See [CONTRIBUTING.md](CONTRIBUTING.md). This project is released under the
[MIT License](LICENSE).
