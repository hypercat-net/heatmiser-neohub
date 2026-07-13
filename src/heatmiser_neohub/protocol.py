"""NeoHub WebSocket message envelope encode/decode."""

from __future__ import annotations

import json
from typing import Any


def encode_command(command: dict[str, Any] | str) -> str:
    """Encode a NeoHub command for the WSS ``COMMAND`` field.

    The hub expects Heatmiser's single-quoted pseudo-JSON (as in the official
    docs: ``{'FIRMWARE':0}``), not standard JSON. Matching ``neohubapi``, we use
    ``str(dict)`` for that format.
    """
    if isinstance(command, str):
        return command
    return str(command)


def build_request(
    token: str, command: dict[str, Any] | str, command_id: int = 1
) -> str:
    """Build a WSS request for ``hm_get_command_queue``.

    The API nests a JSON string inside ``message`` that contains the token and
    command list. ``COMMAND`` is Heatmiser single-quoted pseudo-JSON (see
    :func:`encode_command`).
    """
    inner = {
        "token": token,
        "COMMANDS": [
            {
                "COMMAND": encode_command(command),
                "COMMANDID": command_id,
            }
        ],
    }
    outer = {
        "message_type": "hm_get_command_queue",
        "message": json.dumps(inner, separators=(",", ":")),
    }
    return json.dumps(outer, separators=(",", ":"))


def parse_response(raw: str | bytes) -> dict[str, Any]:
    """Parse a hub WebSocket frame into a structured response.

    Returns a dict with keys:
      - ``command_id``: int
      - ``device_id``: str | None
      - ``message_type``: str
      - ``response``: parsed JSON (dict/list/scalar) or the raw string if not JSON
      - ``raw``: original outer payload
    """
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")

    outer = json.loads(raw)
    response_field = outer.get("response", "")
    parsed: Any = response_field
    if isinstance(response_field, str) and response_field:
        try:
            parsed = json.loads(response_field)
        except json.JSONDecodeError:
            parsed = response_field

    return {
        "command_id": outer.get("command_id"),
        "device_id": outer.get("device_id"),
        "message_type": outer.get("message_type"),
        "response": parsed,
        "raw": outer,
    }
