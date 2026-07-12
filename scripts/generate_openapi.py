#!/usr/bin/env python3
"""Generate OpenAPI 3.1 spec for the IMI Heatmiser NeoHub WebSocket API.

The NeoHub control plane is WSS (not HTTP). This OpenAPI document models each
JSON command as a logical POST under /commands/{name} so Swagger UI can browse
request/response schemas. The real transport is documented in the info section
and the shared WsEnvelope schemas.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "openapi" / "neohub-api.openapi.yaml"

# (name, summary, argument_schema_hint, deprecated, tags, example_value)
# argument_schema_hint: "zero" | "devices" | "string" | "number" | "object" | custom dict schema
Command = tuple[str, str, Any, bool, list[str], Any]

COMMANDS: list[Command] = [
    ("AUTO_MODE_OFF", "Disable automatic fan speed control (neoStat HC)", "devices", False, ["cooling"], "HCtest"),
    ("AWAY_OFF", "Cancel away mode", "devices_or_zero", False, ["global"], 0),
    ("AWAY_ON", "Enable away mode", "devices_or_zero", False, ["global"], 0),
    ("BOOST_OFF", "Boost timeclock off for a duration", "boost", False, ["timeclock"], [{"hours": 1, "minutes": 10}, ["clock"]]),
    ("BOOST_ON", "Boost timeclock on for a duration", "boost", False, ["timeclock"], [{"hours": 1, "minutes": 10}, ["clock"]]),
    ("CANCEL_HGROUP", "Cancel holds for a named hold group id", "string", False, ["hold"], "Box"),
    ("CANCEL_HOLD_ALL", "Cancel all hold commands", "zero", False, ["hold"], 0),
    ("CANCEL_HOLIDAY", "Cancel holiday mode", "zero", False, ["global"], 0),
    ("CLEAR_CURRENT_PROFILE", "Clear active profile id (set to 0) without changing levels", "devices", False, ["profiles"], "kitchen"),
    ("CLEAR_DEVICE_LIST", "Clear and disconnect all devices linked to a zone", "string", False, ["devices"], "Kitchen"),
    ("CLEAR_PROFILE", "Delete a named profile", "string", True, ["profiles"], "winter"),
    ("CLEAR_PROFILE_ID", "Delete a profile by numeric id", "number", False, ["profiles"], 2),
    ("CREATE_GROUP", "Create a command group of zones", "create_group", False, ["groups"], [["lounge", "bed1"], "bob"]),
    ("DELETE_GROUP", "Delete a command group", "string", False, ["groups"], "bob"),
    ("DELETE_RECIPE", "Delete a recipe by name", "string", False, ["recipes"], "test4"),
    ("DETACH_DEVICE", "Detach a device from a zone", "zone_device", False, ["devices"], ["Kitchen", "neoplug"]),
    ("DEVICES_SN", "Return serial numbers for attached devices", "zero", False, ["devices"], 0),
    ("DST_OFF", "Disable automatic daylight saving", "zero", False, ["time"], 0),
    ("DST_ON", "Enable automatic daylight saving (0 or zone code)", "dst_on", False, ["time"], "UK"),
    ("ENGINEERS_DATA", "Deprecated engineers dump", "zero", True, ["deprecated"], 0),
    ("FIRMWARE", "Return neoHub firmware version", "zero", False, ["system"], 0),
    ("FROST_OFF", "Cancel standby / frost protection", "devices", False, ["zones"], ["bed1", "lounge"]),
    ("FROST_ON", "Put zone(s) into standby / frost protection", "devices", False, ["zones"], ["bed1", "lounge"]),
    ("GET_DEVICE_LIST", "List devices linked to a zone", "string", False, ["devices"], "Kitchen"),
    ("GET_DEVICES", "List non-neoStat devices", "zero", False, ["devices"], 0),
    ("GET_ENGINEERS", "Engineers / feature settings cache", "zero", False, ["system"], 0),
    ("GET_GROUPS", "List command groups", "zero", False, ["groups"], 0),
    ("GET_HOLD", "List active holds set by the app", "zero", False, ["hold"], 0),
    ("GET_HOLIDAY", "Get holiday start/end", "zero", False, ["global"], 0),
    ("GET_HOURSRUN", "Hours the output was on per day", "devices", False, ["stats"], "Kitchen"),
    ("GET_LIVE_DATA", "Live status and cache timestamps", "zero", False, ["system"], 0),
    ("GET_PROFILE", "Get a named profile", "string", True, ["profiles"], "kitchen"),
    ("GET_PROFILE_0", "Read profile 0 comfort levels from a device", "devices", False, ["profiles"], "Bathroom"),
    ("GET_PROFILE_NAMES", "List profile names", "zero", True, ["profiles"], 0),
    ("GET_PROFILE_TIMERS", "All timeclock profiles", "zero", False, ["profiles"], 0),
    ("GET_PROFILES", "All thermostat profiles", "zero", False, ["profiles"], 0),
    ("GET_RECIPES", "List stored recipes", "zero", False, ["recipes"], 0),
    ("GET_SYSTEM", "System-wide settings cache", "zero", False, ["system"], 0),
    ("GET_TEMPLOG", "Historical temperatures (15-minute samples)", "devices", False, ["stats"], ["Kitchen"]),
    ("GET_TIMER_0", "Read profile 0 timer levels from a timeclock", "devices", False, ["profiles"], "Timer"),
    ("GET_ZONES", "Zone name to device id map", "zero", False, ["devices"], 0),
    ("GLOBAL_DEV_LIST", "Devices affected by AWAY", "devices", False, ["global"], ["lounge"]),
    ("GLOBAL_SYSTEM_TYPE", "Set global heat/cool system type", "string", False, ["cooling"], "HeatOrCool"),
    ("HOLD", "Hold heating and/or cooling temperature", "hold", False, ["hold"], [{"temp": 16, "hours": 2, "minutes": 30, "id": "Box"}, ["Kitchen"]]),
    ("HOLIDAY", "Enable holiday between start and end timestamps", "holiday", False, ["global"], ["14450001062016", "14450002062016"]),
    ("IDENTIFY", "Flash neoHub link LED", "zero", False, ["system"], 0),
    ("IDENTIFY_DEV", "Flash neoStat LCD backlight", "string", False, ["zones"], "test"),
    ("INFO", "Deprecated live info dump", "zero", True, ["deprecated"], 0),
    ("LINK_DEVICE", "Link a device to a zone", "zone_device", False, ["devices"], ["Kitchen", "neoplug"]),
    ("LOCK", "PIN-lock thermostat(s)", "lock", False, ["zones"], [[1, 2, 3, 4], ["Bathroom", "kitchen"]]),
    ("MANUAL_DST", "Manual daylight saving offset (0 or 1 hour)", "number", False, ["time"], 0),
    ("MANUAL_OFF", "Reinstate neoPlug schedule", "devices", False, ["timeclock"], "plug"),
    ("MANUAL_ON", "Disable neoPlug schedule (manual mode)", "devices", False, ["timeclock"], "plug"),
    ("NTP_OFF", "Disconnect from network time server", "zero", False, ["time"], 0),
    ("NTP_ON", "Reconnect to network time server", "zero", False, ["time"], 0),
    ("PERMIT_JOIN", "Open pairing window for a device or repeater", "permit_join", False, ["devices"], [120, "kitchen"]),
    ("PROFILE_TITLE", "Rename a profile", "name_pair", False, ["profiles"], ["Summer", "Winter"]),
    ("READ_COMFORT_LEVELS", "Deprecated comfort level read", "devices", True, ["deprecated"], "kitchen"),
    ("READ_DCB", "Deprecated DCB read", "number", True, ["deprecated"], 100),
    ("READ_TIMECLOCK", "Read timeclock on/off periods", "devices", False, ["timeclock"], "Hot water"),
    ("REMOVE_REPEATER", "Remove a repeater", "string", False, ["devices"], "repeaternode12345"),
    ("REMOVE_ZONE", "Remove a zone/device from the network", "string", False, ["devices"], "test"),
    ("RESET", "Soft-reboot the neoHub (firmware 2027+)", "zero", False, ["system"], 0),
    ("RUN_PROFILE", "Run a profile by name", "string", True, ["profiles"], "winter"),
    ("RUN_PROFILE_ID", "Push a profile id to devices", "run_profile_id", False, ["profiles"], [25, "Kitchen", "Lounge"]),
    ("RUN_RECIPE", "Run a stored recipe", "run_recipe", False, ["recipes"], ["test2"]),
    ("SET_CHANNEL", "Set ZigBee channel", "number", False, ["system"], 11),
    ("SET_CLOSE_DELAY", "Global window-switch close delay (seconds)", "number", False, ["devices"], 10),
    ("SET_COMFORT_LEVELS", "Deprecated comfort level write", "object", True, ["deprecated"], {}),
    ("SET_COOL_TEMP", "Set cooling setpoint", "temp_devices", False, ["cooling"], [27.5, "HCtest"]),
    ("SET_DATE", "Set calendar date (disables NTP)", "date", False, ["time"], [2018, 12, 9]),
    ("SET_DELAY", "Output delay in minutes", "temp_devices", False, ["engineers"], [5, "test"]),
    ("SET_DIFF", "Switching differential", "temp_devices", False, ["engineers"], [2, ["test"]]),
    ("SET_FAILSAFE", "Enable/disable neoAir RF failsafe", "failsafe", False, ["engineers"], [True, "neoair"]),
    ("SET_FAN_SPEED", "Set fan speed (neoStat HC)", "fan_speed", False, ["cooling"], ["HIGH", ["HCtest"]]),
    ("SET_FLOOR", "Floor temperature limit", "temp_devices", False, ["engineers"], [28, "floor1"]),
    ("SET_FORMAT", "Program format (global)", "string", False, ["system"], "7DAY"),
    ("SET_FROST", "Frost protection temperature", "temp_devices", False, ["engineers"], [9, "test"]),
    ("SET_GLOBAL_HC_MODE", "Global heating/cooling/auto mode", "string", False, ["cooling"], "heating"),
    ("SET_HC_MODE", "Per-device HC mode", "hc_mode", False, ["cooling"], ["COOLING", ["Device1"]]),
    ("SET_LEVEL_4", "Use 4 comfort levels per day", "zero", False, ["system"], 0),
    ("SET_LEVEL_6", "Use 6 comfort levels per day", "zero", False, ["system"], 0),
    ("SET_OPEN_DELAY", "Global window-switch open delay (seconds)", "number", False, ["devices"], 10),
    ("SET_PREHEAT", "Maximum preheat hours", "temp_devices", False, ["engineers"], [3, "Bathroom"]),
    ("SET_RF_MODE", "Wireless sensor mode (mix/remote/self)", "rf_mode", False, ["devices"], ["mix", "Kitchen"]),
    ("SET_TEMP", "Temporary heating setpoint", "temp_devices", False, ["zones"], [21.5, "Zone 3"]),
    ("SET_TEMP_FORMAT", "Celsius or Fahrenheit (global)", "string", False, ["system"], "C"),
    ("SET_TIME", "Set clock time (disables NTP)", "time", False, ["time"], [14, 25]),
    ("SET_TIMECLOCK", "Write timeclock periods", "set_timeclock", False, ["timeclock"], [{}, "Hot water"]),
    ("STATISTICS", "Deprecated statistics", "zero", True, ["deprecated"], 0),
    ("STORE_PROFILE", "Store a named thermostat profile (not neoStat HC)", "object", False, ["profiles"], {"info": {}, "name": "my profile"}),
    ("STORE_PROFILE2", "Store profile and return new ID", "object", False, ["profiles"], {"info": {}, "name": "my profile"}),
    ("STORE_PROFILE_0", "Store comfort levels directly to device(s)", "object", False, ["profiles"], [{}, "bedroom1"]),
    ("STORE_PROFILE_TIMER_0", "Store timer levels directly to timeclock", "object", False, ["profiles"], [{}, "Office"]),
    ("STORE_RECIPE", "Store a named recipe", "object", False, ["recipes"], ["test4", [], ["kitchen"]]),
    ("SUMMER_OFF", "Cancel summer/frost for thermostats", "devices", False, ["zones"], ["Bathroom"]),
    ("SUMMER_ON", "Summer frost for thermostats only", "devices", False, ["zones"], ["lounge", "bed1"]),
    ("TIME_ZONE", "Timezone offset from GMT", "number", False, ["time"], 0),
    ("TIMER_HOLD_OFF", "Override timeclock off for N minutes", "timer_hold", False, ["timeclock"], [15, "clock"]),
    ("TIMER_HOLD_ON", "Override timeclock on for N minutes", "timer_hold", False, ["timeclock"], [15, "clock"]),
    ("TIMER_OFF", "Turn neoPlug/timeclock output off", "devices", False, ["timeclock"], "plug"),
    ("TIMER_ON", "Turn neoPlug/timeclock output on", "devices", False, ["timeclock"], "plug"),
    ("UNLOCK", "Unlock PIN-locked thermostat(s)", "devices", False, ["zones"], ["Bathroom", "kitchen"]),
    ("USER_LIMIT", "Limit on-device setpoint adjustments", "temp_devices", False, ["zones"], [5, ["bed1", "lounge"]]),
    ("VIEW_ROC", "View rate-of-change (minutes per degree)", "devices", False, ["stats"], ["Bathroom1"]),
    ("ZONE_TITLE", "Rename a zone", "name_pair", False, ["devices"], ["HCtest", "HCtest2"]),
]


def devices_schema() -> dict[str, Any]:
    return {
        "oneOf": [
            {"type": "string", "description": "Single zone/device/group name"},
            {"type": "integer", "description": "Device id"},
            {
                "type": "array",
                "items": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                "description": "List of zone/device/group names or ids",
            },
            {"type": "integer", "const": 0, "description": "Affect all devices (where supported)"},
        ]
    }


def arg_schema(hint: Any) -> dict[str, Any]:
    if isinstance(hint, dict):
        return hint
    if hint == "zero":
        return {"type": "integer", "const": 0}
    if hint == "devices":
        return devices_schema()
    if hint == "devices_or_zero":
        return devices_schema()
    if hint == "string":
        return {"type": "string"}
    if hint == "number":
        return {"type": "number"}
    if hint == "object":
        return {"type": "object", "additionalProperties": True}
    if hint == "boost":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {
                    "type": "object",
                    "required": ["hours", "minutes"],
                    "properties": {
                        "hours": {"type": "integer"},
                        "minutes": {"type": "integer"},
                    },
                },
                devices_schema(),
            ],
        }
    if hint == "create_group":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "array", "items": {"type": "string"}},
                {"type": "string", "description": "Group name"},
            ],
        }
    if hint == "zone_device":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "string", "description": "Zone name"},
                {"type": "string", "description": "Device name"},
            ],
        }
    if hint == "dst_on":
        return {
            "oneOf": [
                {"type": "integer", "const": 0},
                {"type": "string", "enum": ["UK", "EU", "NZ"]},
            ]
        }
    if hint == "hold":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {
                    "type": "object",
                    "properties": {
                        "temp": {"type": "number"},
                        "cool": {"type": "number"},
                        "hours": {"type": "integer"},
                        "minutes": {"type": "integer"},
                        "id": {"type": "string"},
                    },
                },
                devices_schema(),
            ],
        }
    if hint == "holiday":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {
                "type": "string",
                "pattern": "^[0-9]{14}$",
                "description": "HHMMSSDDMMYYYY",
            },
        }
    if hint == "lock":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 4,
                    "items": {"type": "integer", "minimum": 0, "maximum": 9},
                },
                devices_schema(),
            ],
        }
    if hint == "permit_join":
        return {
            "oneOf": [
                {
                    "type": "array",
                    "prefixItems": [
                        {"type": "integer", "description": "Seconds"},
                        {"type": "string", "description": "Zone name"},
                    ],
                    "minItems": 2,
                    "maxItems": 2,
                },
                {
                    "type": "array",
                    "prefixItems": [
                        {"type": "string", "const": "repeater"},
                        {"type": "integer", "description": "Seconds"},
                    ],
                    "minItems": 2,
                    "maxItems": 2,
                },
            ]
        }
    if hint == "name_pair":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {"type": "string"},
        }
    if hint == "run_profile_id":
        return {
            "type": "array",
            "minItems": 2,
            "prefixItems": [{"type": "integer", "description": "Profile id"}],
            "items": {"oneOf": [{"type": "integer"}, {"type": "string"}]},
        }
    if hint == "run_recipe":
        return {
            "type": "array",
            "minItems": 1,
            "prefixItems": [{"type": "string", "description": "Recipe name"}],
            "items": True,
        }
    if hint == "temp_devices":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "number"},
                devices_schema(),
            ],
        }
    if hint == "date":
        return {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "prefixItems": [
                {"type": "integer"},
                {"type": "integer", "minimum": 1, "maximum": 12},
                {"type": "integer", "minimum": 1, "maximum": 31},
            ],
        }
    if hint == "time":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "integer", "minimum": 0, "maximum": 23},
                {"type": "integer", "minimum": 0, "maximum": 59},
            ],
        }
    if hint == "failsafe":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "boolean"},
                {"type": "string"},
            ],
        }
    if hint == "fan_speed":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "string", "enum": ["HIGH", "MED", "LOW", "OFF", "AUTO"]},
                devices_schema(),
            ],
        }
    if hint == "hc_mode":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "string", "enum": ["HEATING", "COOLING", "AUTO", "VENT"]},
                devices_schema(),
            ],
        }
    if hint == "rf_mode":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "string", "enum": ["mix", "remote", "self", "MIX", "REMOTE", "SELF"]},
                devices_schema(),
            ],
        }
    if hint == "timer_hold":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "integer", "description": "Minutes (0 cancels)"},
                devices_schema(),
            ],
        }
    if hint == "set_timeclock":
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "prefixItems": [
                {"type": "object", "additionalProperties": True},
                devices_schema(),
            ],
        }
    return {"description": "Command argument"}


def yaml_escape(value: str) -> str:
    if any(c in value for c in ":#{}[],&*?|>!%@`'\""):
        return json.dumps(value)
    return value


def to_yaml(data: Any, indent: int = 0) -> str:
    """Minimal YAML emitter good enough for OpenAPI (no anchors)."""
    sp = "  " * indent
    if isinstance(data, dict):
        if not data:
            return "{}"
        lines: list[str] = []
        for key, value in data.items():
            key_s = str(key)
            if isinstance(value, (dict, list)):
                if value == {}:
                    lines.append(f"{sp}{key_s}: {{}}")
                elif value == []:
                    lines.append(f"{sp}{key_s}: []")
                else:
                    lines.append(f"{sp}{key_s}:")
                    lines.append(to_yaml(value, indent + 1))
            elif value is None:
                lines.append(f"{sp}{key_s}: null")
            elif isinstance(value, bool):
                lines.append(f"{sp}{key_s}: {'true' if value else 'false'}")
            elif isinstance(value, (int, float)):
                lines.append(f"{sp}{key_s}: {value}")
            else:
                text = str(value)
                if "\n" in text:
                    lines.append(f"{sp}{key_s}: |")
                    for line in text.splitlines():
                        lines.append(f"{sp}  {line}")
                else:
                    lines.append(f"{sp}{key_s}: {yaml_escape(text)}")
        return "\n".join(lines)
    if isinstance(data, list):
        if not data:
            return f"{sp}[]"
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                rendered = to_yaml(item, indent + 1)
                first, *rest = rendered.splitlines()
                lines.append(f"{sp}- {first.lstrip()}")
                for line in rest:
                    lines.append(line)
            elif isinstance(item, bool):
                lines.append(f"{sp}- {'true' if item else 'false'}")
            elif isinstance(item, (int, float)):
                lines.append(f"{sp}- {item}")
            else:
                lines.append(f"{sp}- {yaml_escape(str(item))}")
        return "\n".join(lines)
    raise TypeError(type(data))


def build_spec() -> dict[str, Any]:
    tags = sorted(
        {
            tag
            for *_, tag_list, __ in COMMANDS
            for tag in tag_list
        }
    )

    paths: dict[str, Any] = {
        "/ws": {
            "get": {
                "operationId": "connectWebSocket",
                "tags": ["transport"],
                "summary": "Open persistent WSS connection",
                "description": (
                    "Connect to `wss://{host}:4243`. Disable TLS certificate "
                    "verification (hub uses a locally generated cert). After "
                    "connect, send `WsRequest` frames and receive `WsResponse` frames.\n\n"
                    "This path is documentary: OpenAPI cannot execute WebSocket "
                    "handshakes in Swagger UI."
                ),
                "parameters": [
                    {
                        "name": "host",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string", "example": "192.168.0.19"},
                    }
                ],
                "responses": {
                    "101": {
                        "description": "Switching Protocols (WebSocket established)",
                    }
                },
            }
        }
    }

    for name, summary, hint, deprecated, cmd_tags, example in COMMANDS:
        command_body = {name: example}
        paths[f"/commands/{name}"] = {
            "post": {
                "operationId": f"command_{name}",
                "tags": cmd_tags,
                "summary": summary,
                "deprecated": deprecated,
                "description": (
                    f"Send NeoHub command `{name}` over the authenticated WSS "
                    f"envelope. The logical HTTP mapping exists only for documentation.\n\n"
                    f"**Inner command JSON:** `{json.dumps(command_body)}`"
                ),
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": [name],
                                "additionalProperties": False,
                                "properties": {name: arg_schema(hint)},
                            },
                            "example": command_body,
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": (
                            "Hub reply after unwrapping `WsResponse.response` "
                            "(payload shape varies by command)."
                        ),
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CommandResult"}
                            }
                        },
                    }
                },
            }
        }

    # Highlight primary read commands with richer response schemas
    paths["/commands/GET_LIVE_DATA"]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] = {"$ref": "#/components/schemas/LiveData"}
    paths["/commands/GET_SYSTEM"]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] = {"$ref": "#/components/schemas/SystemInfo"}

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "IMI Heatmiser NeoHub API",
            "version": "3.02",
            "summary": "WebSocket JSON command API for IMI Heatmiser neoHub systems",
            "description": (
                "Unofficial OpenAPI representation of the IMI Heatmiser neoHub API "
                "(Rev 3.02 / document header Rev 3.01, released 01/03/2023).\n\n"
                "## Transport\n\n"
                "- **Primary:** Secure WebSocket `wss://{host}:4243` with API token "
                "auth (Neo App → Settings → Api Access → Tokens).\n"
                "- Ignore TLS certificate verification (local self-signed cert).\n"
                "- **Discovery:** UDP broadcast `hubseek` to port `19790`.\n"
                "- **Legacy:** TCP port `4242` (often disabled on firmware 2153+).\n\n"
                "## Message envelope\n\n"
                "Every command is wrapped as:\n\n"
                "```json\n"
                "{\n"
                '  \"message_type\": \"hm_get_command_queue\",\n'
                '  \"message\": \"{\\\"token\\\":\\\"…\\\",\\\"COMMANDS\\\":[{\\\"COMMAND\\\":\\\"{\\\\\\\"GET_LIVE_DATA\\\\\\\":0}\\\",\\\"COMMANDID\\\":1}]}\"\n'
                "}\n"
                "```\n\n"
                "Responses use `message_type: hm_set_command_response` with a "
                "stringified JSON `response` field.\n\n"
                "## Related links\n\n"
                "- [neoHub smart control](https://www.heatmiser.com/neohub-smart-control/)\n"
                "- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)\n"
                "- [Official NeoHub API PDF](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf)\n\n"
                "The original IMI Heatmiser documentation is proprietary; this OpenAPI "
                "file is a community mapping for tooling and the heatmiser-neohub "
                "client library."
            ),
            "license": {
                "name": "Documentation derived from proprietary IMI Heatmiser materials",
                "url": "https://www.heatmiser.com/",
            },
            "contact": {
                "name": "IMI Heatmiser Developer Portal",
                "url": "https://dev.heatmiser.com/",
            },
        },
        "servers": [
            {
                "url": "wss://{host}:4243",
                "description": "NeoHub WebSocket (TLS verify disabled)",
                "variables": {
                    "host": {
                        "default": "192.168.0.19",
                        "description": "NeoHub IP or hostname on the LAN",
                    }
                },
            }
        ],
        "tags": [
            {"name": "transport", "description": "Connection and framing"},
            {"name": "system", "description": "Hub system / caches"},
            {"name": "devices", "description": "Zones, pairing, accessories"},
            {"name": "zones", "description": "Per-zone thermostat controls"},
            {"name": "profiles", "description": "Comfort and timer profiles"},
            {"name": "global", "description": "Away / holiday / global lists"},
            {"name": "hold", "description": "Temporary temperature holds"},
            {"name": "timeclock", "description": "Timers and neoPlug"},
            {"name": "cooling", "description": "neoStat HC heating/cooling"},
            {"name": "time", "description": "Clock, NTP, DST, timezone"},
            {"name": "engineers", "description": "Engineers / feature settings"},
            {"name": "groups", "description": "Command groups"},
            {"name": "recipes", "description": "Stored command recipes"},
            {"name": "stats", "description": "Runtime and temperature logs"},
            {"name": "deprecated", "description": "Deprecated — avoid in new designs"},
        ]
        + [{"name": t} for t in tags if t not in {
            "transport", "system", "devices", "zones", "profiles", "global",
            "hold", "timeclock", "cooling", "time", "engineers", "groups",
            "recipes", "stats", "deprecated",
        }],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "NeoHubToken": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-NeoHub-Token",
                    "description": (
                        "Logical representation of the token embedded in the WSS "
                        "`message` JSON (`token` field). Not an HTTP header on the wire."
                    ),
                }
            },
            "schemas": {
                "WsRequest": {
                    "type": "object",
                    "required": ["message_type", "message"],
                    "properties": {
                        "message_type": {
                            "type": "string",
                            "const": "hm_get_command_queue",
                        },
                        "message": {
                            "type": "string",
                            "description": (
                                "JSON string: {token, COMMANDS:[{COMMAND, COMMANDID}]}"
                            ),
                        },
                    },
                    "example": {
                        "message_type": "hm_get_command_queue",
                        "message": (
                            '{"token":"YOUR_TOKEN","COMMANDS":['
                            '{"COMMAND":"{\\"GET_LIVE_DATA\\":0}","COMMANDID":1}]}'
                        ),
                    },
                },
                "WsResponse": {
                    "type": "object",
                    "properties": {
                        "command_id": {"type": "integer"},
                        "device_id": {"type": "string"},
                        "message_type": {
                            "type": "string",
                            "const": "hm_set_command_response",
                        },
                        "response": {
                            "type": "string",
                            "description": "JSON-encoded command result",
                        },
                    },
                    "example": {
                        "command_id": 1,
                        "device_id": "D8:80:39:AD:0D:F0",
                        "message_type": "hm_set_command_response",
                        "response": '{"firmware version":"2153"}',
                    },
                },
                "CommandResult": {
                    "description": "Parsed contents of WsResponse.response",
                    "oneOf": [
                        {"type": "object", "additionalProperties": True},
                        {"type": "array"},
                        {"type": "string"},
                        {"type": "number"},
                        {"type": "boolean"},
                    ],
                },
                "HubseekResponse": {
                    "type": "object",
                    "properties": {
                        "ip": {"type": "string", "example": "192.168.0.19"},
                        "device_id": {
                            "type": "string",
                            "example": "D8:80:39:AD:0D:F0",
                        },
                    },
                },
                "DeviceLive": {
                    "type": "object",
                    "properties": {
                        "ZONE_NAME": {"type": "string"},
                        "DEVICE_ID": {"type": "integer"},
                        "ACTUAL_TEMP": {"type": "string"},
                        "SET_TEMP": {"type": "string"},
                        "COOL_TEMP": {"type": "number"},
                        "HEAT_ON": {"type": "boolean"},
                        "COOL_ON": {"type": "boolean"},
                        "HEAT_MODE": {"type": "boolean"},
                        "COOL_MODE": {"type": "boolean"},
                        "STANDBY": {"type": "boolean"},
                        "AWAY": {"type": "boolean"},
                        "HOLIDAY": {"type": "boolean"},
                        "OFFLINE": {"type": "boolean"},
                        "LOW_BATTERY": {"type": "boolean"},
                        "LOCK": {"type": "boolean"},
                        "WINDOW_OPEN": {"type": "boolean"},
                        "HOLD_ON": {"type": "boolean"},
                        "HOLD_TEMP": {"type": "number"},
                        "HOLD_TIME": {"type": "string"},
                        "THERMOSTAT": {"type": "boolean"},
                        "TIMECLOCK": {"type": "boolean"},
                        "TIMER_ON": {"type": "boolean"},
                        "ACTIVE_PROFILE": {"type": "integer"},
                        "ACTIVE_LEVEL": {"type": "integer"},
                        "HC_MODE": {"type": "string"},
                        "FAN_SPEED": {"type": "string"},
                        "FAN_CONTROL": {"type": "string"},
                        "CURRENT_FLOOR_TEMPERATURE": {"type": "number"},
                        "FLOOR_LIMIT": {"type": "boolean"},
                        "WRITE_COUNT": {"type": "integer"},
                        "RECENT_TEMPS": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                "LiveData": {
                    "type": "object",
                    "properties": {
                        "HUB_TIME": {"type": "integer"},
                        "HUB_AWAY": {"type": "boolean"},
                        "HUB_HOLIDAY": {"type": "boolean"},
                        "HOLIDAY_END": {"type": "integer"},
                        "GLOBAL_SYSTEM_TYPE": {"type": "string"},
                        "CLOSE_DELAY": {"type": "integer"},
                        "OPEN_DELAY": {"type": "integer"},
                        "COOL_INPUT": {"type": "boolean"},
                        "TIMESTAMP_SYSTEM": {"type": "integer"},
                        "TIMESTAMP_DEVICE_LISTS": {"type": "integer"},
                        "TIMESTAMP_ENGINEERS": {"type": "integer"},
                        "TIMESTAMP_PROFILE_0": {"type": "integer"},
                        "TIMESTAMP_PROFILE_COMFORT_LEVELS": {"type": "integer"},
                        "TIMESTAMP_PROFILE_TIMERS": {"type": "integer"},
                        "TIMESTAMP_PROFILE_TIMERS_0": {"type": "integer"},
                        "devices": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/DeviceLive"},
                        },
                    },
                },
                "SystemInfo": {
                    "type": "object",
                    "properties": {
                        "DEVICE_ID": {"type": "string"},
                        "HUB_VERSION": {"type": "integer"},
                        "HUB_TYPE": {
                            "type": "integer",
                            "description": "1=G1, 2=G2 HomeKit, 3=neoAir Hub / Mini",
                        },
                        "CORF": {"type": "string", "enum": ["C", "F"]},
                        "FORMAT": {"type": "integer"},
                        "ALT_TIMER_FORMAT": {"type": "integer"},
                        "HEATING_LEVELS": {"type": "integer"},
                        "HEATORCOOL": {"type": "string"},
                        "TIME_ZONE": {"type": "number"},
                        "UTC": {"type": "integer"},
                        "TIMESTAMP": {"type": "integer"},
                        "NTP_ON": {"type": "string"},
                        "DST_AUTO": {"type": "boolean"},
                        "DST_ON": {"type": "boolean"},
                        "PARTITION": {"type": "string"},
                        "TIMEZONESTR": {"type": "string"},
                    },
                },
            },
        },
        "security": [{"NeoHubToken": []}],
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    spec = build_spec()
    header = (
        "# Generated by scripts/generate_openapi.py — do not edit by hand.\n"
        "# Source: docs/reference/neohub-api-rev-3.02.md (IMI Heatmiser NeoHub API Rev 3.02)\n"
    )
    OUT.write_text(header + to_yaml(spec) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes, {len(COMMANDS)} commands)")


if __name__ == "__main__":
    main()
