# NeoHub OpenAPI

`neohub-api.openapi.yaml` is an OpenAPI 3.1 description of the IMI Heatmiser NeoHub
control API for browsing in Swagger UI and similar tools.

The real transport is a WebSocket (WSS) JSON session on port `4243`, not HTTP.
Each NeoHub command is modelled as a logical `POST /commands/{NAME}` so request
and response schemas can be documented. Treat those paths as a catalogue of
command envelopes, not as REST endpoints you call over HTTP.

## Related links

- [neoHub smart control (product)](https://www.heatmiser.com/neohub-smart-control/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)
- [Official NeoHub API PDF](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf)
- Local guide: [`../neohub-api-rev-3.02.md`](../neohub-api-rev-3.02.md)

Regenerate the committed YAML with:

```bash
python scripts/generate_openapi.py
```
