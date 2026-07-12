# CLI (`neohub`)

The package installs a `neohub` console script for discovery and debugging against
a live hub.

## Install

```bash
pip install heatmiser-neohub
# or from a checkout:
pip install -e .
```

Docker (multi-arch image
[`hypercat42/heatmiser-neohub`](https://hub.docker.com/r/hypercat42/heatmiser-neohub)):

```bash
docker run --rm hypercat42/heatmiser-neohub --help
```

## Configuration

Copy [`.env.example`](https://github.com/hypercat-net/heatmiser-neohub/blob/main/.env.example)
to `.env` in your working directory, or export variables / pass flags.

| Variable | Flag | Description | Default |
| --- | --- | --- | --- |
| `NEOHUB_HOST` | `--host` | Hub hostname or IP. If unset, auto-discovers when exactly one hub is on the LAN. | *(auto)* |
| `NEOHUB_TOKEN` | `--token` | API token from Neo App → Settings → Api Access → Tokens | *(required for commands)* |
| `NEOHUB_PORT` | `--port` | WSS port | `4243` |

The CLI loads `.env` automatically via `python-dotenv` (real environment variables win).

## Commands

```bash
# List NeoHubs on the LAN (UDP hubseek on port 19790)
neohub discover

# Live zone/device status (GET_LIVE_DATA)
neohub live-data

# System cache (GET_SYSTEM)
neohub system

# Arbitrary JSON command
neohub cmd '{"FIRMWARE":0}'
```

Examples with explicit connection settings:

```bash
neohub live-data --host 192.168.0.19 --token "$NEOHUB_TOKEN"
neohub cmd '{"GET_ZONES":0}' --host 192.168.0.19 --token "$NEOHUB_TOKEN"
```

### Auto-discovery

If `--host` / `NEOHUB_HOST` is omitted, the CLI runs UDP `hubseek` and:

- uses the hub when **exactly one** responds
- errors if **none** or **more than one** are found (set the host explicitly)

Port defaults to **4243** when unset.

### Docker and discovery

UDP broadcast does not leave Docker’s default bridge network. On Linux, use host
networking for `discover` (and for auto-discover when the host is unset):

```bash
docker run --rm --network host hypercat42/heatmiser-neohub discover
docker run --rm --env-file .env hypercat42/heatmiser-neohub live-data
```

On Docker Desktop (macOS/Windows), prefer setting `NEOHUB_HOST` explicitly.
