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

## Releases (PyPI and Docker)

Git tags are the release identity. Keep them aligned:

1. Bump `version` in `pyproject.toml` (and `__version__` in
   `src/heatmiser_neohub/__init__.py`) to `X.Y.Z`.
2. Commit, push `main`, then tag and push `vX.Y.Z`.

That tag drives both channels:

| Channel | Workflow | Artifact |
| --- | --- | --- |
| PyPI | `.github/workflows/pypi.yaml` | `heatmiser-neohub==X.Y.Z` |
| Docker Hub | `.github/workflows/docker.yaml` | `hypercat42/heatmiser-neohub:vX.Y.Z` |

The Docker image installs from the **git checkout** at that tag (`pip install .`
in the Dockerfile), not from PyPI. Alignment comes from building both from the
same tag — so `pip install heatmiser-neohub==X.Y.Z` and
`docker pull …:vX.Y.Z` contain the same code.

Notes:

- Tagged releases (`v*`) re-run Tests before PyPI upload and before pushing
  `:vX.Y.Z` to Docker Hub. Docker `latest` / SHA builds on `main` do not wait
  on that gate (PRs already run Tests separately).
- `latest` / short SHA tags on Docker Hub also update on pushes to `main`; those
  can be ahead of the last PyPI release. Prefer `:vX.Y.Z` when you need a match.
- PyPI can also be triggered manually (`workflow_dispatch`); still use a version
  bump + tag for a normal release.
- Trusted Publishing uses GitHub Environment `pypi` (no API token secret).

## Reporting issues

Use GitHub Issues and include:

- OS / Python version
- Hub firmware or model if known
- Steps to reproduce and any redacted CLI output
