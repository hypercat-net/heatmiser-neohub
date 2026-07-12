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
```

If you change the OpenAPI command catalogue in `scripts/generate_openapi.py`,
regenerate and commit the YAML locally (CI does not run the generator):

```bash
python scripts/generate_openapi.py
```

## Pull requests

- Keep changes focused and describe *why* in the PR body.
- Prefer small PRs over large mixed ones.
- Do not commit secrets (`.env`, tokens, hub credentials).
- OpenAPI: edit `scripts/generate_openapi.py`, run the generator, commit both
  the script and `docs/openapi/neohub-api.openapi.yaml`.

## Releases (PyPI)

Version bumps live in `pyproject.toml`. Tagging `v*` (or running the **PyPI**
workflow manually) builds an sdist/wheel and uploads via Trusted Publishing
(`.github/workflows/pypi.yaml`, GitHub Environment `pypi`).

## Reporting issues

Use GitHub Issues and include:

- OS / Python version
- Hub firmware or model if known
- Steps to reproduce and any redacted CLI output
