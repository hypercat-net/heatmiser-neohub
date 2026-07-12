# Security Policy

## Supported versions

Security fixes are applied to the latest release on `main`.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security problems.

Instead, report privately via GitHub Security Advisories for this repository
(**Security → Report a vulnerability**), or contact the maintainers directly.

Include:

- A description of the issue and impact
- Steps to reproduce
- Affected versions / commit if known

We will acknowledge the report and work on a fix as promptly as practical.

## Notes

- NeoHub API tokens grant local control of a heating system — treat them as secrets.
- The hub uses a locally generated TLS certificate; clients disable certificate
  verification by design (LAN-only trust model documented by IMI Heatmiser).
