# Contributing

Thanks for contributing to **heatmiser-neohub**.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # then set NEOHUB_TOKEN (and optionally NEOHUB_HOST)
```

## Checks before opening a PR

```bash
pytest
python scripts/generate_openapi.py   # if you changed the command catalogue
```

## Pull requests

- Keep changes focused and describe *why* in the PR body.
- Prefer small PRs over large mixed ones.
- Do not commit secrets (`.env`, tokens, hub credentials).
- The OpenAPI YAML is generated — edit `scripts/generate_openapi.py`, then regenerate.

## Reporting issues

Use GitHub Issues and include:

- OS / Python version
- Hub firmware or model if known
- Steps to reproduce and any redacted CLI output
