"""Tests for message envelope encode/decode and model parsing."""

from __future__ import annotations

import json

from heatmiser_neohub.models import Device, LiveData, SystemInfo
from heatmiser_neohub.protocol import build_request, parse_response


def test_build_request_wraps_command_and_token() -> None:
    raw = build_request("secret-token", {"GET_SYSTEM": 0}, command_id=7)
    outer = json.loads(raw)

    assert outer["message_type"] == "hm_get_command_queue"

    inner = json.loads(outer["message"])
    assert inner["token"] == "secret-token"
    assert len(inner["COMMANDS"]) == 1

    command_entry = inner["COMMANDS"][0]
    assert command_entry["COMMANDID"] == 7
    assert json.loads(command_entry["COMMAND"]) == {"GET_SYSTEM": 0}


def test_build_request_default_command_id() -> None:
    raw = build_request("t", {"GET_LIVE_DATA": 0})
    inner = json.loads(json.loads(raw)["message"])
    assert inner["COMMANDS"][0]["COMMANDID"] == 1


def test_parse_response_decodes_nested_json_string() -> None:
    frame = json.dumps(
        {
            "command_id": 3,
            "device_id": "abc123",
            "message_type": "hm_set_command_response",
            "response": json.dumps({"HUB_TIME": 1700000000}),
        }
    )

    parsed = parse_response(frame)

    assert parsed["command_id"] == 3
    assert parsed["device_id"] == "abc123"
    assert parsed["message_type"] == "hm_set_command_response"
    assert parsed["response"] == {"HUB_TIME": 1700000000}
    assert parsed["raw"]["command_id"] == 3


def test_parse_response_accepts_bytes() -> None:
    frame = json.dumps({"command_id": 1, "response": json.dumps({"ok": True})})
    parsed = parse_response(frame.encode("utf-8"))
    assert parsed["response"] == {"ok": True}


def test_parse_response_keeps_non_json_response_as_string() -> None:
    frame = json.dumps({"command_id": 1, "response": "not json"})
    parsed = parse_response(frame)
    assert parsed["response"] == "not json"


def test_parse_response_missing_response_field_defaults_to_empty_string() -> None:
    frame = json.dumps({"command_id": 1})
    parsed = parse_response(frame)
    assert parsed["response"] == ""


def test_round_trip_build_and_parse() -> None:
    request = build_request("tok", {"GET_SYSTEM": 0}, command_id=42)
    outer = json.loads(request)
    inner = json.loads(outer["message"])
    command_id = inner["COMMANDS"][0]["COMMANDID"]

    hub_reply = json.dumps(
        {
            "command_id": command_id,
            "message_type": "hm_set_command_response",
            "response": json.dumps({"DEVICE_ID": "hub-1"}),
        }
    )
    parsed = parse_response(hub_reply)
    assert parsed["command_id"] == 42
    assert parsed["response"] == {"DEVICE_ID": "hub-1"}


def test_device_from_dict_maps_fields() -> None:
    device = Device.from_dict(
        {
            "ZONE_NAME": "Lounge",
            "DEVICE_ID": "5",
            "ACTUAL_TEMP": "21.5",
            "SET_TEMP": "20",
            "HEAT_ON": True,
            "AWAY": "false",
            "LOW_BATTERY": 0,
            "CURRENT_FLOOR_TEMPERATURE": "127",
            "ACTIVE_PROFILE": "2",
        }
    )

    assert device.zone_name == "Lounge"
    assert device.device_id == 5
    assert device.actual_temp == 21.5
    assert device.set_temp == 20.0
    assert device.heat_on is True
    assert device.away is False
    assert device.low_battery is False
    # 127 is the hub's sentinel for "no floor sensor"
    assert device.floor_temp is None
    assert device.active_profile == 2


def test_device_from_dict_defaults_when_empty() -> None:
    device = Device.from_dict({})
    assert device.zone_name == ""
    assert device.device_id is None
    assert device.actual_temp is None
    assert device.heat_on is False


def test_live_data_from_dict_parses_devices() -> None:
    data = LiveData.from_dict(
        {
            "HUB_TIME": 1700000000,
            "HUB_AWAY": True,
            "HUB_HOLIDAY": False,
            "devices": [
                {"ZONE_NAME": "Lounge", "DEVICE_ID": "1"},
                {"ZONE_NAME": "Bedroom", "DEVICE_ID": "2"},
                "not-a-device",
            ],
        }
    )

    assert data.hub_time == 1700000000
    assert data.hub_away is True
    assert data.hub_holiday is False
    assert len(data.devices) == 2
    assert data.devices[0].zone_name == "Lounge"
    assert data.devices[1].zone_name == "Bedroom"


def test_live_data_from_dict_defaults_with_no_devices() -> None:
    data = LiveData.from_dict({})
    assert data.devices == []
    assert data.hub_away is False


def test_system_info_from_dict_maps_fields() -> None:
    info = SystemInfo.from_dict(
        {
            "DEVICE_ID": "hub-1",
            "HUB_VERSION": 2410,
            "CORF": "C",
            "DST_AUTO": True,
            "DST_ON": "1",
            "TIME_ZONE": "0",
        }
    )

    assert info.device_id == "hub-1"
    assert info.hub_version == 2410
    assert info.corf == "C"
    assert info.dst_auto is True
    assert info.dst_on is True
    assert info.time_zone == 0.0
