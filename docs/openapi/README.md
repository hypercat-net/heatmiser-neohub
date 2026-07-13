# NeoHub OpenAPI

`neohub-api.openapi.yaml` is a **committed** OpenAPI 3.1 description of the IMI
Heatmiser NeoHub control API for browsing in Swagger UI and similar tools. CI
publishes this file as-is; it does not regenerate it.

The real transport is a WebSocket (WSS) JSON session on port `4243`, not HTTP.
Each NeoHub command is modelled as a logical `POST /commands/{NAME}` so request
and response schemas can be documented. Treat those paths as a catalogue of
command envelopes, not as REST endpoints you call over HTTP.

The outer WSS frame is [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) JSON.
The nested `COMMAND` string value is Heatmiser single-quoted pseudo-JSON
(e.g. `{'GET_LIVE_DATA': 0}`), not double-quoted JSON — see the API reference
section on COMMAND quoting.

## Related links

- [neoHub smart control (product)](https://www.heatmiser.com/neohub-smart-control/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)
- [Official NeoHub API PDF](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf)
- Local guide: [`../reference/neohub-api-rev-3.02.md`](../reference/neohub-api-rev-3.02.md)

## Regenerating locally

Prefer editing `scripts/generate_openapi.py` (command catalogue), then rewrite
the YAML and commit both:

```bash
python scripts/generate_openapi.py
```

Do not edit `neohub-api.openapi.yaml` by hand unless you intend to stop using
the generator.
