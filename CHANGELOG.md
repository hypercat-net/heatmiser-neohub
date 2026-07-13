# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-13

### Added

- Public package exports for discovery helpers and `NeoHubTimeoutError`
- `Device.available_modes` / `supports_mode()`, plus humidity, preheat, and
  modulation fields from `GET_LIVE_DATA`
- Coverage gate (90%) with expanded client, CLI, and discovery unit tests
- Protocol documentation for Heatmiser `COMMAND` quoting vs RFC 8259 JSON

### Changed

- CLI `--port` annotated as optional (matches env/default behaviour)

### Stability

Version 1.0 freezes the public client, models, discovery helpers, and CLI
commands (`discover`, `live-data`, `system`, `cmd`). It does **not** promise
typed wrappers for every NeoHub command, WebSocket auto-reconnect, or raising
on hub application-error payloads (those remain returned response data).

## [0.1.3] - 2026-07-13

- CLI `--version` / `--verbose` / `--debug` and related logging

## [0.1.2] - 2026-07-13

- Fix WSS `COMMAND` encoding (Heatmiser single-quoted form; avoids hub
  `Invalid Json` errors)

## [0.1.1] - 2026-07-12

- Packaging and docs polish; Docker builds from git checkout

## [0.1.0] - 2026-07-12

- Initial library, CLI, docs, and CI
