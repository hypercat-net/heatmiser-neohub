"""Typed models for NeoHub cache responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _as_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


@dataclass(slots=True)
class Device:
    """A zone/device entry from ``GET_LIVE_DATA``."""

    zone_name: str
    device_id: int | None = None
    actual_temp: float | None = None
    set_temp: float | None = None
    cool_temp: float | None = None
    heat_on: bool = False
    cool_on: bool = False
    cool_mode: bool = False
    heat_mode: bool = False
    standby: bool = False
    away: bool = False
    holiday: bool = False
    offline: bool = False
    low_battery: bool = False
    lock: bool = False
    window_open: bool = False
    hold_on: bool = False
    hold_temp: float | None = None
    hold_time: str | None = None
    thermostat: bool = False
    timeclock: bool = False
    timer_on: bool = False
    active_profile: int | None = None
    active_level: int | None = None
    hc_mode: str | None = None
    fan_speed: str | None = None
    fan_control: str | None = None
    floor_temp: float | None = None
    floor_limit: bool = False
    write_count: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Device:
        floor = data.get("CURRENT_FLOOR_TEMPERATURE")
        floor_temp = _as_float(floor)
        # Hub uses 127 as a sentinel for "no floor sensor"
        if floor_temp == 127.0:
            floor_temp = None

        return cls(
            zone_name=str(data.get("ZONE_NAME") or data.get("zone_name") or ""),
            device_id=int(data["DEVICE_ID"]) if data.get("DEVICE_ID") is not None else None,
            actual_temp=_as_float(data.get("ACTUAL_TEMP")),
            set_temp=_as_float(data.get("SET_TEMP")),
            cool_temp=_as_float(data.get("COOL_TEMP")),
            heat_on=_as_bool(data.get("HEAT_ON")),
            cool_on=_as_bool(data.get("COOL_ON")),
            cool_mode=_as_bool(data.get("COOL_MODE")),
            heat_mode=_as_bool(data.get("HEAT_MODE")),
            standby=_as_bool(data.get("STANDBY")),
            away=_as_bool(data.get("AWAY")),
            holiday=_as_bool(data.get("HOLIDAY")),
            offline=_as_bool(data.get("OFFLINE")),
            low_battery=_as_bool(data.get("LOW_BATTERY")),
            lock=_as_bool(data.get("LOCK")),
            window_open=_as_bool(data.get("WINDOW_OPEN")),
            hold_on=_as_bool(data.get("HOLD_ON")),
            hold_temp=_as_float(data.get("HOLD_TEMP")),
            hold_time=data.get("HOLD_TIME"),
            thermostat=_as_bool(data.get("THERMOSTAT")),
            timeclock=_as_bool(data.get("TIMECLOCK")),
            timer_on=_as_bool(data.get("TIMER_ON")),
            active_profile=(
                int(data["ACTIVE_PROFILE"])
                if data.get("ACTIVE_PROFILE") is not None
                else None
            ),
            active_level=(
                int(data["ACTIVE_LEVEL"]) if data.get("ACTIVE_LEVEL") is not None else None
            ),
            hc_mode=data.get("HC_MODE"),
            fan_speed=data.get("FAN_SPEED"),
            fan_control=data.get("FAN_CONTROL"),
            floor_temp=floor_temp,
            floor_limit=_as_bool(data.get("FLOOR_LIMIT")),
            write_count=(
                int(data["WRITE_COUNT"]) if data.get("WRITE_COUNT") is not None else None
            ),
            raw=data,
        )


@dataclass(slots=True)
class LiveData:
    """Parsed ``GET_LIVE_DATA`` response."""

    hub_time: int | None = None
    hub_away: bool = False
    hub_holiday: bool = False
    holiday_end: int | None = None
    global_system_type: str | None = None
    close_delay: int | None = None
    open_delay: int | None = None
    cool_input: bool = False
    timestamp_system: int | None = None
    timestamp_device_lists: int | None = None
    timestamp_engineers: int | None = None
    timestamp_profile_0: int | None = None
    timestamp_profile_comfort_levels: int | None = None
    timestamp_profile_timers: int | None = None
    timestamp_profile_timers_0: int | None = None
    devices: list[Device] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LiveData:
        devices_raw = data.get("devices") or []
        devices = [
            Device.from_dict(item)
            for item in devices_raw
            if isinstance(item, dict)
        ]
        return cls(
            hub_time=data.get("HUB_TIME"),
            hub_away=_as_bool(data.get("HUB_AWAY")),
            hub_holiday=_as_bool(data.get("HUB_HOLIDAY")),
            holiday_end=data.get("HOLIDAY_END"),
            global_system_type=data.get("GLOBAL_SYSTEM_TYPE"),
            close_delay=data.get("CLOSE_DELAY"),
            open_delay=data.get("OPEN_DELAY"),
            cool_input=_as_bool(data.get("COOL_INPUT")),
            timestamp_system=data.get("TIMESTAMP_SYSTEM"),
            timestamp_device_lists=data.get("TIMESTAMP_DEVICE_LISTS"),
            timestamp_engineers=data.get("TIMESTAMP_ENGINEERS"),
            timestamp_profile_0=data.get("TIMESTAMP_PROFILE_0"),
            timestamp_profile_comfort_levels=data.get("TIMESTAMP_PROFILE_COMFORT_LEVELS"),
            timestamp_profile_timers=data.get("TIMESTAMP_PROFILE_TIMERS"),
            timestamp_profile_timers_0=data.get("TIMESTAMP_PROFILE_TIMERS_0"),
            devices=devices,
            raw=data,
        )


@dataclass(slots=True)
class SystemInfo:
    """Parsed ``GET_SYSTEM`` response."""

    device_id: str | None = None
    hub_version: int | None = None
    hub_type: int | None = None
    corf: str | None = None
    format: int | None = None
    alt_timer_format: int | None = None
    heating_levels: int | None = None
    heat_or_cool: str | None = None
    time_zone: float | None = None
    utc: int | None = None
    timestamp: int | None = None
    ntp_on: str | None = None
    dst_auto: bool = False
    dst_on: bool = False
    partition: str | None = None
    timezonestr: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SystemInfo:
        return cls(
            device_id=data.get("DEVICE_ID"),
            hub_version=data.get("HUB_VERSION"),
            hub_type=data.get("HUB_TYPE"),
            corf=data.get("CORF"),
            format=data.get("FORMAT"),
            alt_timer_format=data.get("ALT_TIMER_FORMAT"),
            heating_levels=data.get("HEATING_LEVELS"),
            heat_or_cool=data.get("HEATORCOOL"),
            time_zone=_as_float(data.get("TIME_ZONE")),
            utc=data.get("UTC"),
            timestamp=data.get("TIMESTAMP"),
            ntp_on=data.get("NTP_ON"),
            dst_auto=_as_bool(data.get("DST_AUTO")),
            dst_on=_as_bool(data.get("DST_ON")),
            partition=data.get("PARTITION"),
            timezonestr=data.get("TIMEZONESTR"),
            raw=data,
        )
