# neoHub API Rev 3.02

> Source: [Official NeoHub API PDF (IMI Heatmiser)](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf)  
> Document header: neoHub API Rev 3.01 — Released 01/03/2023  
> Complete API guide to using the IMI Heatmiser neoHub system and associated devices.

## Related links

- [neoHub smart control (product)](https://www.heatmiser.com/neohub-smart-control/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)
- [Official NeoHub API PDF (IMI Heatmiser)](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf)

## Table of contents

- [Revision history](#revision-history)
- [Copyright](#copyright)
- [Notes to reader](#notes-to-reader)
- [Websocket port 4243 connections](#websocket-port-4243-connections)
- [Legacy port 4242 connections](#legacy-port-4242-connections)
- [Websocket command structure](#websocket-command-structure)
- [JSON commands (legacy)](#json-commands-legacy)
- [V2 commands overview](#v2-commands-overview)
- [neoHub commands](#neohub-commands)
- [Caches and data stores](#caches-and-data-stores)
- [Comfort levels](#comfort-levels)
- [Time and date settings](#time-and-date-settings)
- [Adding devices](#adding-thermostats-devices-and-accessories)
- [Devices, switches and sensors](#devices)
- [Profiles](#profiles)
- [Boost, engineers, groups and holds](#boost-function)
- [Time clock and neoPlug commands](#time-clock-commands)
- [Recipes](#recipes)
- [Set temperature and cooling](#set-temperature)
- [Appendix A — Profile examples](#appendix-a--profiles)
- [Appendix B — Deprecated commands](#appendix-b--deprecated-commands)
- [Appendix C — Alphabetical command list](#appendix-c--alphabetical-command-list)
- [Appendix D — Cached file examples](#appendix-d--examples-of-cached-files)
- [Appendix E — Device types](#appendix-e--neo-system-device-type-list)
- [Appendix F — Daylight saving](#appendix-f--daylight-saving)
- [Addendum](#addendum)

---

## Revision history

| Revision | Notes |
| --- | --- |
| Rev 0 | Original version taken from V1 system |
| Rev 1.000 | V2 commands added |
| Rev 1.001 | Web sockets added |
| Rev 2.000 | Cooling commands, new data caches |
| REV 2.501 | Reformatted to include more examples, descriptions and references |
| REV 2.502 | Added HomeKit flag and `HUB_TYPE` variable |
| REV 2.503 | Added Addendum page 47 |
| REV 2.504 | Minor correction to grouped commands; added hub type variable to addendum |
| REV 2.505 | Updated hold command to include cooling |
| REV 2.507 | Clarified Progformat settings |
| REV 2.508 | Time Zone List added in Appendix F |
| REV 2.509 | Correction to wireless sensor example page 16 |
| REV 2.510 | Added missing JSON command |
| REV 2.511 | Updated Store_Profile command |
| REV 2.512 | Correction to Hold command |
| REV 2.700 | 0.5 degree switching / recipes added |
| REV 2.701 | Fixed errors in recipe commands |
| REV 2.8 | Fixed errors in hold command |
| REV 2.9 | Added examples of 0.5 switching in Set Temp |
| REV 2.91 | Added warning: Do Not Use `STORE_PROFILE` or `STORE_PROFILE2` with neoStat HC |
| REV 3.0 | Adding new websocket comms method and token generation |
| REV 3.2 | New default settings in Appendix A |

---

## Copyright

This document contains proprietary information that is protected by copyright. This document must not be reproduced, transcribed, stored, translated or transmitted, in part or in whole, without the prior written approval of IMI Heatmiser.

---

## Notes to reader

Apps normally connect through the webserver but it is possible to check commands directly by talking to the neoHub.

Historically this was done by direct connection to the neoHub established using TCP/IP on **port 4242**. This port, although still currently available, has been superseded by a new websocket communications port **4243**.

For all neoHubs running firmware **2153**, the Legacy API Port on 4242 is closed but can be enabled in the IMI Heatmiser neoApp via the Settings / API Access Menu.

Data from each device is stored as an array called a **DCB**. The JSON commands access these arrays and report the data back; any error relating to a DCB access should be taken as a failure to read the data from the target device.

Each device can be set up as a thermostat or a time clock. The `{"GET_LIVE_DATA":0}` command will return `timeclock = true` for time clocks.

The neoAir wireless device can also be set up as a combined device that has both a timeclock and thermostat; these are reported as 2 separate devices. The word **Timer** is automatically appended to the zone title for the neoAir Timeclock.

Several existing commands have been deprecated; these are listed in [Appendix B](#appendix-b--deprecated-commands). For backward compatibility they will still function but should not be used in new designs.

---

## Websocket port 4243 connections

### IP address discovery

Finding neoHubs on the local network: UDP broadcast `hubseek` on port **19790** prompts hubs to respond with their IP if available. Third-party systems need to broadcast and listen for UDP on port 19790.

**Request:**

```bash
echo -n "hubseek" | nc -b -u 255.255.255.255 19790
```

**Response:**

```json
{"ip":"192.168.0.19", "device_id":"D8:80:39:AD:0D:F0"}
```

### Authentication

Users manage access to their neoHub by generating API tokens for third-party systems. Create tokens in the IMI Heatmiser Neo App via **Settings > Api Access > Tokens** (available from all apps after version *\<Insert version\>*). Share the token with the third-party system.

### Connection

Connection is via **WSS** (secure WebSocket) on port **4243**. Because the security certificate is generated locally and assigned to an IP, WSS clients should **ignore certificate verification**. Once connected, the connection is constant — there should be no need to reconnect.

Commands must include the auth token in a JSON string sent to the hub.

**Example URI:** `wss://192.168.0.18:4243`

---

## Legacy port 4242 connections

### Putty

When using Putty, any command must be followed by **CTRL+SHIFT+@** pressed simultaneously, then Enter. Send the data as **RAW**.

Examples:

- `{"GET_SYSTEM":0}` followed by CTRL+SHIFT+@ — returns current system settings
- `{"GET_ZONES":0}` followed by CTRL+SHIFT+@ — returns the list of zone names

---

## Websocket command structure

### Syntax description

Websocket commands take this format:

```json
{
  "message_type": "hm_get_command_queue",
  "message": "{\"token\":\"{{token}}\",\"COMMANDS\":[{\"COMMAND\":\"{{command}}\",\"COMMANDID\":1}]}"
}
```

| Placeholder | Meaning |
| --- | --- |
| `{{command}}` | Takes the format `{'FIRMWARE':0}` — all commands in this document (Appendix C) can be included |
| `{{token}}` | Token provided by the user |

Anything within the `message` section must remain **escaped**.

#### COMMAND quoting vs standard JSON

The outer WebSocket frame and the nested `message` object are [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) JSON (strings use double quotes, U+0022). The value of each `COMMAND` field is **not** standard JSON: Heatmiser documents it as a single-quoted pseudo-JSON object such as `{'FIRMWARE':0}`.

Per RFC 8259 §7, a JSON string is wrapped in quotation marks (U+0022), and JSON object member names/strings likewise use double quotes. A payload of the form `{"FIRMWARE":0}` is therefore valid JSON, but the NeoHub rejects that form inside `COMMAND` with `{"error":"Invalid Json"}`. Use the Heatmiser single-quoted form instead (this library encodes it with Python `str(dict)`, matching `neohubapi`).

| Layer | Format | Example |
| --- | --- | --- |
| Outer WSS frame | RFC 8259 JSON | `{"message_type":"hm_get_command_queue","message":"…"}` |
| Nested `message` | RFC 8259 JSON (as a string) | `{"token":"…","COMMANDS":[…]}` |
| `COMMAND` value | Heatmiser single-quoted form | `{'GET_LIVE_DATA': 0}` |

**Sample response:**

```json
{
  "command_id": 1,
  "device_id": "D8:80:39:AD:0D:F0",
  "message_type": "hm_set_command_response",
  "response": "{\"firmware version\":\"2153\"}"
}
```

Further examples: [Postman collection](https://heatmiser.postman.co/workspace/95e2f560-f892-42fb-a1f6-e88f929028df)

---

## JSON commands (legacy)

### Syntax description

| Placeholder | Meaning |
| --- | --- |
| `<device(s)>` | A device, an array of devices and/or group names, or a group name — e.g. `"device1"`, `["device1","device2","ourgroup"]`, or `"ourgroup"` |
| `<group>` | Always a group name like `"ourgroup"` |
| `<* name>` | The name as a string `"name"` |
| `<temp>` | Integer or floating-point value |

**Basic structures:**

```json
{"cmd":0}
{"cmd":<arg>}
{"cmd":[<args>]}
```

When `devices` is one argument:

```json
{"cmd":[1,"kitchen"]}
{"cmd":[1,["kitchen", "bathroom"]]}
{"cmd":"kitchen"}
{"cmd":["kitchen"]}
```

Such commands only check that there are enough arguments (and the correct contents).

---

## V2 commands overview

### Changes to the system

V2 avoids downloading or uploading unchanged data. Data is broken into sections; each section includes a timestamp. Constantly changing data is in the **live data** array, which also contains timestamps for all other sections.

To display current information, download live data only. Scan timestamps; if they match previously downloaded values, nothing further is needed. If timestamps changed, re-download the associated cache.

Synchronisation relies on correct use and interpretation of timestamps.

### Switching levels

Thermostats can have **4 or 6** comfort levels (global user setting).

### Profiles

Profiles are numbered and named so only the profile number needs to be sent. The user selects by name locally; the app sends the profile number. The neoHub uses its copy to send comfort levels or timeclock settings to devices.

The neoStat reports the profile it is currently using as part of live data.

#### Profile 0

Profile 0 is not a real profile — it reports changes made on the thermostat itself and allows single-room app changes. If a device was on a named profile and the user manually changes settings, the live-data profile byte resets to **0**. Profile 0 is a copy of comfort levels for a device not running a named profile. Named profiles **1–255** are available.

### Device types

Device types describe physical form and how to interpret live data / caches. Examples: neoStat = type 1 (thermostat or timeclock); neoAir = type 7 (thermostat, timeclock, or both); repeaters = type 10. Full list: [Appendix E](#appendix-e--neo-system-device-type-list).

---

## neoHub commands

### System reboot

```json
{"RESET":0}
```

Soft reboot. Firmware **2027** and above only.

### Set channel

Change the ZigBee channel:

```json
{"SET_CHANNEL":11}
```

Allowed channels: **11, 14, 15, 19, 20, 24, 25**.

Ensure all neoAirs / neoStats are online when changing channel, or they may need re-pairing. If the hub detects interference it may refuse the change — verify via the system cache.

`READ_DCB:100` (system-wide variables) is **deprecated** — use `{"GET_SYSTEM":0}`.

### System-wide (global) settings

Some neoStat features are global (e.g. °C / °F). Changing them updates every device.

```json
{"SET_TEMP_FORMAT":"C"}
{"SET_TEMP_FORMAT":"F"}
```

Changing C↔F invalidates historical data (automatically deleted).

```json
{"SET_FORMAT":"7DAY"}
```

Changing format on one device changes it on all connected devices.

| Format string | Meaning | System cache `FORMAT` |
| --- | --- | --- |
| `"NONPROGRAMMABLE"` | Fixed temperature | 0 |
| `"24HOURSFIXED"` | Every day the same | 1 |
| `"5DAY/2DAY"` | Weekdays / weekends | 2 |
| `"7DAY"` | Every day different | 4 |

Time clocks cannot be nonprogrammable. If the system moves to nonprogrammable, timeclocks remain on previous settings. Read via `"ALT_TIMER_FORMAT"` in the system cache.

Changing program format invalidates stored profiles (automatically deleted).

### Global functions

#### Away

For unoccupied property of unknown duration. Puts timeclocks and thermostats into standby. Thermostats maintain frost protection; timeclocks stay off.

```json
{"AWAY_ON":0}
{"AWAY_OFF":0}
{"AWAY_ON":["lounge","bed1"]}
{"AWAY_OFF":["lounge","bed1"]}
```

`{"AWAY_OFF":0}` cancels targeted away — prefer `FROST_ON` / `FROST_OFF` for individual rooms.

#### Holiday

Unoccupied until a specified date/time. Same standby behaviour as Away.

```json
{"HOLIDAY":["HHMMSSDDMMYYYY","HHMMSSDDMMYYYY"]}
```

Example:

```json
{"HOLIDAY":["14450001062016","14450002062016"]}
```

Start: 14:45:00 on 01/06/2016; end: 14:45:00 on 02/06/2016.

```json
{"GET_HOLIDAY":0}
```

Example response:

```json
{"end": "Sun Feb 11 19:02:00 2018\n","ids": ["Office"],"start": "Fri Feb 9 14:33:29 2018\n"}
```

```json
{"CANCEL_HOLIDAY":0}
```

---

## Caches and data stores

Seven rarely changing data blocks are stored in the neoHub (and typically cached by the app):

1. System
2. Device lists
3. Engineers data
4. Profile_0
5. Profile_comfort levels
6. Profile_timers
7. Profile_timers_0

When a command affects stored data, the cache and its timestamp update; the timestamp is copied into live data. Controllers upload a cache only when its timestamp is newer.

### Live data

Contains latest thermostat status and timestamps for all caches. Updated about every **90 seconds** (more often when an app is connected to the server).

```json
{"GET_LIVE_DATA":0}
```

Example (abridged):

```json
{
  "CLOSE_DELAY": 0,
  "COOL_INPUT": false,
  "GLOBAL_SYSTEM_TYPE": "HeatOnly",
  "HOLIDAY_END": 0,
  "HUB_AWAY": false,
  "HUB_HOLIDAY": false,
  "HUB_TIME": 1518613752,
  "OPEN_DELAY": 0,
  "TIMESTAMP_DEVICE_LISTS": 1518607836,
  "TIMESTAMP_ENGINEERS": 1518607837,
  "TIMESTAMP_PROFILE_0": 1518607836,
  "TIMESTAMP_PROFILE_COMFORT_LEVELS": 1518604883,
  "TIMESTAMP_PROFILE_TIMERS": 1518600089,
  "TIMESTAMP_PROFILE_TIMERS_0": 1518607918,
  "TIMESTAMP_SYSTEM": 1518607836,
  "devices": [
    {
      "ACTIVE_LEVEL": 2,
      "ACTIVE_PROFILE": 25,
      "ACTUAL_TEMP": "25.7",
      "AVAILABLE_MODES": ["heat"],
      "AWAY": false,
      "COOL_MODE": false,
      "COOL_ON": false,
      "COOL_TEMP": 0,
      "CURRENT_FLOOR_TEMPERATURE": 127,
      "DATE": "Wednesday",
      "DEVICE_ID": 1,
      "FAN_CONTROL": "Automatic",
      "FAN_SPEED": "Custom",
      "FLOOR_LIMIT": false,
      "HC_MODE": "VENT",
      "HEAT_MODE": true,
      "HEAT_ON": false,
      "HOLD_OFF": true,
      "HOLD_ON": false,
      "HOLD_TEMP": 5,
      "HOLD_TIME": "0:00",
      "HOLIDAY": false,
      "LOCK": false,
      "LOW_BATTERY": false,
      "MANUAL_OFF": true,
      "MODELOCK": false,
      "MODULATION_LEVEL": 0,
      "OFFLINE": false,
      "PIN_NUMBER": "1111",
      "PREHEAT_ACTIVE": false,
      "RECENT_TEMPS": ["25.6", "25.7"],
      "SET_TEMP": "17.0",
      "STANDBY": false,
      "SWITCH_DELAY_LEFT": "0:00",
      "TEMPORARY_SET_FLAG": false,
      "THERMOSTAT": true,
      "TIME": "13:08",
      "TIMER_ON": false,
      "WINDOW_OPEN": false,
      "WRITE_COUNT": 110,
      "ZONE_NAME": "Bathroom"
    }
  ]
}
```

Not all variables apply to every device (e.g. `LOCK` is always false on a neoPlug). `WRITE_COUNT` increments when a command is received and actioned.

For sleepy end devices, write-count bits 6 and 7 indicate the hub received a command but is waiting for the device to wake; the hub simulates the expected response until outstanding commands complete.

### System cache

```json
{"GET_SYSTEM":0}
```

Example (neoHub version 2081):

```json
{
  "ALT_TIMER_FORMAT": 2,
  "CORF": "C",
  "DEVICE_ID": "neoHub",
  "DST_AUTO": true,
  "DST_ON": false,
  "FORMAT": 2,
  "HEATING_LEVELS": 4,
  "HEATORCOOL": "HeatOnly",
  "HUB_VERSION": 2081,
  "NTP_ON": "Running",
  "PARTITION": "4",
  "TIMESTAMP": 1518607836,
  "TIME_ZONE": 0,
  "UTC": 1518611554
}
```

### Device lists

`TIMESTAMP_DEVICE_LISTS` tracks additions/removals. Related commands: `GET_DEVICES`, `GET_DEVICE_LIST`, `GET_ZONES`, `DEVICES_SN`.

```json
{"GET_ZONES":0}
```

```json
{"Bathroom": 1, "Room name ": 2, "Office": 3, "plug": 4}
```

```json
{"GET_DEVICES":0}
```

Returns non-neoStat devices, e.g. `{"result": ["plug"]}`.

```json
{"GET_DEVICE_LIST":"room name"}
{"DEVICES_SN":0}
```

### Engineers data

```json
{"GET_ENGINEERS":0}
```

Example:

```json
{
  "Bathroom": {
    "DEADBAND": 0,
    "DEVICE_ID": 1,
    "DEVICE_TYPE": 1,
    "FLOOR_LIMIT": 28,
    "FROST_TEMP": 12,
    "MAX_PREHEAT": 3,
    "OUTPUT_DELAY": 0,
    "PUMP_DELAY": 0,
    "RF_SENSOR_MODE": "self",
    "STAT_FAILSAFE": 0,
    "STAT_VERSION": 101,
    "SWITCHING DIFFERENTIAL": 1,
    "SWITCH_DELAY": 0,
    "SYSTEM_TYPE": 0,
    "TIMESTAMP": 1518535921,
    "USER_LIMIT": 0,
    "WINDOW_SWITCH_OPEN": false
  }
}
```

### Profile timestamps

| Timestamp | Meaning | Access |
| --- | --- | --- |
| `TIMESTAMP_PROFILE_COMFORT_LEVELS` | Saved thermostat profiles | — |
| `TIMESTAMP_PROFILE_TIMERS` | Saved timeclock profiles | — |
| `TIMESTAMP_PROFILE_0` | Change on any device profile 0 (comfort) | `{"GET_PROFILE_0":<device>}` |
| `TIMESTAMP_PROFILE_TIMERS_0` | Change on any device profile 0 (timer) | `{"GET_TIMER_0":<device>}` |

If a device has no active profile and comfort/timer timestamps are newer, update that device’s cache. If it has an active profile and those timestamps are not newer, no update is needed.

---

## Comfort levels

A comfort level is time + temperature (heating/cooling systems: four variables). The thermostat targets the temperature at the stated time until the next level.

Default: **4** levels/day; can increase to **6**. A group of comfort levels is a **Profile**.

```json
{"SET_LEVEL_4":0}
{"SET_LEVEL_6":0}
```

```json
{"READ_COMFORT_LEVELS":<device(s)>}
```

Deprecated — use `GET_PROFILE_0`.

```json
{"SET_COMFORT_LEVELS":<device(s)>}
```

Deprecated — use `STORE_PROFILE_0`.

A switching time of **24:00** or **00:00** disables that level; temperature stays at the last valid level (shown as `--` on the thermostat).

### GLOBAL_DEV_LIST

Contains ID numbers of devices affected by the `AWAY` command.

---

## Time and date settings

The neoHub connects to NTP for GMT by default. If disabled, set time/date manually. Built-in clock syncs devices; backup battery keeps the clock for ~4 hours without power.

UTC appears in system cache; `HUB_TIME` in live data includes DST and timezone (shown on neoStats).

```json
{"NTP_OFF":0}
{"NTP_ON":0}
```

```json
{"SET_DATE":[2018, 12, 09]}
{"SET_TIME":[14, 25]}
```

Setting time/date manually turns NTP off.

### Time zone

```json
{"TIME_ZONE":10.5}
{"TIME_ZONE":-5.0}
```

Offsets from GMT; `.5` for half-hour zones. Can adjust in 15-minute steps via timezone alone (UTC + zone + DST).

### Daylight savings

Full details: [Appendix F](#appendix-f--daylight-saving).

When turning automatic DST off, also send `{"MANUAL_DST":0}`.

```json
{"MANUAL_DST":0}
{"MANUAL_DST":1}
```

- `0` → neoHub time = GMT + timezone (no DST)
- `1` → neoHub time = GMT + timezone + 1 hour

---

## Adding thermostats, devices and accessories

```json
{"PERMIT_JOIN":[120,"kitchen"]}
```

120 seconds to pair a device named kitchen.

Repeaters use a different form:

```json
{"PERMIT_JOIN":["repeater", 120]}
```

Repeaters appear as `repeaternodexxxxx`. Status is in live data. Remove carefully — the same repeater can be added multiple times with new IDs while old status remains until properly removed.

### Zone title / remove

```json
{"ZONE_TITLE":["HCtest","HCtest2"]}
{"REMOVE_ZONE":"test"}
{"REMOVE_REPEATER":<repeater>}
```

If `REMOVE_ZONE` fails to reach the neoStat before hub deletion completes, factory-reset the neoStat before re-pairing. neoPlugs flash a red LED every 20 seconds when disconnected (no Wi‑Fi symbol).

---

## Devices

neoStats are **zones**; anything else (neoPlug, door switch, remote sensor, etc.) is a **Device**. Devices can be linked to zones.

```json
{"GET_DEVICES":0}
{"LINK_DEVICE":[<zone>,<device>]}
{"LINK_DEVICE":["Kitchen ","neoplug"]}
{"GET_DEVICE_LIST":"zone name"}
{"DETACH_DEVICE":["zone name ","device name "]}
{"DEVICES_SN":0}
{"CLEAR_DEVICE_LIST":"Kitchen"}
```

`DETACH_DEVICE` breaks the link but both remain on the system. `CLEAR_DEVICE_LIST` deletes all items in a zone’s device list and disconnects them.

### Window and door switches

Battery wireless open/close switches. Linked to a room, they put the thermostat into standby while open. Global delays:

```json
{"SET_CLOSE_DELAY":10}
{"SET_OPEN_DELAY":X}
```

Add via permit join (shows as a zone). One switch can serve multiple zones.

### Wireless sensors

Battery temperature sensors — monitor, average with neoStat, or replace neoStat sensor:

```json
{"SET_RF_MODE":[<mode>, <devices>]}
{"SET_RF_MODE":["mix", "Kitchen"]}
```

| Mode | Behaviour |
| --- | --- |
| `MIX` | Average of remote sensor(s) and neoStat internal sensor |
| `REMOTE` | Use remote sensor temperature |
| `SELF` | neoStat uses internal sensor; wireless sensor monitors only |

If the sensor loses connection, the neoStat reconnects its internal sensor after **10 minutes**. Multiple sensors: average of all wireless sensors, then average with neoStat (`MIX`) or use as reading (`REMOTE`).

---

## Profiles

Profiles are collections of comfort levels or timeclock switching times. Layout depends on program mode and levels/day:

| Mode | 4 levels | 6 levels |
| --- | --- | --- |
| 7-day | 28 comfort levels | 42 |
| 5/2-day | 8 | 12 |
| 24-hour | 4 | 6 |

Profiles cannot be used in nonprogrammable mode. Changing program mode or levels deletes saved profiles.

**Timeclocks** always have 4 on and 4 off times (regardless of comfort levels):

| Mode | On/off pairs |
| --- | --- |
| 7-day | 28 on + 28 off |
| 5/2-day | 8 + 8 |
| 24-hour | 4 + 4 |

### Clear current profile

Sets profile ID to 0 without changing settings (device leaves the shared-profile “group”):

```json
{"CLEAR_CURRENT_PROFILE":"kitchen"}
```

### JSON structures within profiles

4 levels use `wake`, `leave`, `return`, `sleep`. 6 levels use `wake`, `level1`–`level4`, `sleep` (backward compatible).

**Pre-2079:** `"wake":["07:00",21]`  
**From 2079:** `"wake":["10:00",25.0,0.0,false]` → `[time, temp1, temp2, enable temp2]`

Temperatures are floats for 0.5° setpoints; older hardware rounds down. All levels must be included and match hub settings. Complete examples: [Appendix A](#appendix-a--profiles) / Appendix C.

### Saving profiles

> **Do not use `STORE_PROFILE` / `STORE_PROFILE2` with neoStat HC — use `STORE_PROFILE_0`.**

```json
{"STORE_PROFILE":{"info":{...}, "name":"my profile"}}
{"STORE_PROFILE2":{"info":{...}, "name":"my profile"}}
```

`STORE_PROFILE2` returns `{"ID": 3,"result": "profile created"}`.

### Retrieving profiles

```json
{"GET_PROFILE_NAMES":0}
{"GET_PROFILES":0}
{"GET_PROFILE_TIMERS":0}
{"GET_PROFILE":"kitchen"}
{"GET_PROFILE":"Timer"}
{"PROFILE_TITLE":["Summer","Winter"]}
```

### Editing profiles

Load, then overwrite with the same **`ID`** field (not `PROFILE_ID` — that creates a new ID and stops devices updating):

```json
{"STORE_PROFILE": {"ID": 25, "info": {...}, "name": "ball"}}
```

### Activating / deleting

```json
{"RUN_PROFILE_ID":[25,"Kitchen","Lounge"]}
{"CLEAR_PROFILE":"winter"}
{"CLEAR_PROFILE_ID":2}
```

### Profile 0 (device-local)

```json
{"GET_PROFILE_0":"Bathroom"}
{"GET_TIMER_0":"Timer"}
{"STORE_PROFILE_0":[{...},"bedroom1"]}
{"STORE_PROFILE_TIMER_0":[{...},"Office"]}
```

Deprecated (still valid for compatibility):

- `{"STORE_PROFILE":<profile ob>}`
- `{"CLEAR_PROFILE":<profile name>}`
- `{"GET_PROFILE":<profile name>}`
- `{"RUN_PROFILE":<profile name>}`
- `{"GET_PROFILE_NAMES":0}`

---

## Boost function

Override a timeclock on/off for a fixed duration:

```json
{"BOOST_ON":[{"hours":1,"minutes":10},["floor1","clock"]]}
{"BOOST_ON":[{"hours":0,"minutes":0},["floor1","clock"]]}
{"BOOST_OFF":[{"hours":1,"minutes":10},["floor1","clock"]]}
{"BOOST_OFF":[{"hours":0,"minutes":0},["floor1","clock"]]}
```

### Engineers settings

Remote edits of selected feature-menu settings (target device only):

```json
{"SET_DIFF":[2,["test"]]}
{"SET_FLOOR":[28, "floor1"]}
{"SET_PREHEAT":[3,["test"]]}
{"SET_FROST":[9,"test"]}
{"SET_DELAY":[5, "test"]}
{"SET_FAILSAFE":[true, "neoair"]}
{"SET_FAILSAFE":[false, "neoair"]}
{"FIRMWARE":0}
```

Failsafe (neoAir): if no RF signal for 50 minutes, heating on 12 minutes every hour.

### Create group

```json
{"CREATE_GROUP":[["lounge","bed1"], "bob"]}
{"GET_GROUPS":0}
{"DELETE_GROUP":"bob"}
{"CANCEL_HGROUP":<group>}
```

### Hold function

Maintain temperature for a fixed time. Named via `"id"` for multiple holds.

```json
{"HOLD":[{"temp":16, "hours":2, "minutes":30,"id":"Box"}, [<devices>]]}
{"HOLD":[{"cool":24, "hours":2, "minutes":30, "id":"Box"}, [<devices>]]}
{"HOLD":[{"temp":16, "cool":24, "hours":2, "minutes":30, "id":"Box"}, [<devices>]]}
{"HOLD":[{"temp":16, "cool":24, "hours":0, "minutes":0, "id":"Box"}, [<devices>]]}
{"CANCEL_HOLD_ALL":0}
{"CANCEL_HGROUP":"id"}
{"GET_HOLD":0}
```

Hours/minutes `0` cancels (other fields ignored). `GET_HOLD` returns holds set by the app, not on-device.

### Identify

```json
{"IDENTIFY":0}
{"IDENTIFY_DEV":"test"}
```

Flashes neoHub link LED / neoStat LCD backlight.

```json
{"INFO":0}
```

Deprecated — use `GET_LIVE_DATA`.

### Lock

```json
{"LOCK":[[1,2,3,4], ["Bathroom","kitchen"]]}
{"UNLOCK":["Bathroom","kitchen"]}
```

### Standby (frost)

```json
{"FROST_ON":["bed1","lounge"]}
{"FROST_OFF":["bed1","lounge"]}
```

Disables schedule; thermostats use frost temp (max settable 17°C while active). Timeclocks: schedule off, output off.

### Summer

Frost for thermostats only (no effect on timeclocks):

```json
{"SUMMER_ON":["lounge","bed1"]}
{"SUMMER_OFF":["Bathroom"]}
```

### Statistics

```json
{"GET_HOURSRUN":"Kitchen"}
{"GET_TEMPLOG":["Kitchen"]}
{"STATISTICS":0}
```

`STATISTICS` is deprecated. Temp log: up to 96 readings/day for 7 days + today (15‑minute intervals).

### HomeKit / HUB_TYPE

`"Homekit": true` indicates Apple HomeKit compatibility (contact Apple for details). This flag will be deprecated in favour of `HUB_TYPE` in system cache / server login data:

| Value | Device |
| --- | --- |
| 1 | Generation 1 neoHub |
| 2 | Generation 2 neoHub (HomeKit) |
| 3 | neoHub Mini |

---

## Time clock commands

### TIMER_HOLD_ON / OFF

```json
{"TIMER_HOLD_ON":[15, "clock"]}
{"TIMER_HOLD_ON":[0, "clock"]}
{"TIMER_HOLD_OFF":[15, "clock"]}
{"TIMER_HOLD_OFF":[0, "clock"]}
```

### neoPlug

Same timeclock structure, plus:

```json
{"MANUAL_ON":<devices>}
{"MANUAL_OFF":<devices>}
{"TIMER_ON":"plug"}
{"TIMER_OFF":"plug"}
```

`MANUAL_ON` disables the built-in schedule (simple on/off via `TIMER_ON` / `TIMER_OFF`). `MANUAL_OFF` reinstates the schedule.

### READ_TIMECLOCK / SET_TIMECLOCK

```json
{"READ_TIMECLOCK":"Hot water"}
{"SET_TIMECLOCK":[<levels>, <device(s)>]}
```

Structure: device → weekday → `time1`–`time4` → `[start, end]`.

### User limit

Restrict button adjustments around the programmed temperature (useful when locked):

```json
{"USER_LIMIT":[5, ["bed1","lounge"]]}
{"USER_LIMIT":[0, ["bed1","lounge"]]}
```

`0` removes the restriction on unlocked stats and restores full lock behaviour on locked devices.

### Optimisation / ROC

```json
{"SET_PREHEAT":[3, "Bathroom"]}
{"VIEW_ROC":["Bathroom1","HCtest"]}
```

Optimum start preheats before the next comfort level. ROC = minutes per degree (rate of change).

---

## Recipes

Named lists of commands stored on the neoHub. Use `DEVICES` as a placeholder; default devices are supplied at store time.

```json
{"STORE_RECIPE":[<name>,[<commands>],[<default devices>]]}
{"STORE_RECIPE":["test4",["{\"SET_TEMP\":[30,DEVICES]}", "{\"LOCK\":[[1,2,3,4],DEVICES]}"],["kitchen","lounge"]]}
{"RUN_RECIPE":["test2"]}
{"RUN_RECIPE":["test2", ["living room","kitchen"]]}
{"DELETE_RECIPE":<name>}
{"GET_RECIPES":0}
```

To edit: copy → modify → delete original → save. Duplicate names are allowed but only the last is used; deleting removes all with that name.

---

## Set temperature

Temporary until the next comfort level (except non-programmable mode). Use Hold for longer overrides.

```json
{"SET_TEMP":[9.0,"Zone 3"]}
{"SET_TEMP":[34.5,["Zone 3","Zone 4"]]}
```

### Cooling (neoStat HC)

Requires up-to-date neoHub firmware. Comfort level structure:

```text
[time, heating temperature, cooling temperature, cooling enabled]
```

Example: `"wake":["10:00",25.0,28.0,true]`

Mixing neoStat and neoStat HC is allowed; neoStats ignore cooling fields.

Every device must share the same mode, or all must be independent.

#### Setup

**Step 1 — Global system type:**

```json
{"GLOBAL_SYSTEM_TYPE":"HeatOrCool"}
{"GLOBAL_SYSTEM_TYPE":"CoolOnly"}
{"GLOBAL_SYSTEM_TYPE":"Independent"}
```

**Step 2 — Global HC mode:**

| System type | Allowed |
| --- | --- |
| HeatOrCool | `heating`, `cooling` |
| CoolOnly | `cooling` |
| Independent | `heating`, `cooling`, `auto` |

```json
{"SET_GLOBAL_HC_MODE":"heating"}
```

**Step 3 — Per-device mode** (required for Independent; automatic for other types):

```json
{"SET_HC_MODE":["COOLING", ["Device1","device2"]]}
{"SET_HC_MODE":["HEATING", ["Device1","device2"]]}
{"SET_HC_MODE":["AUTO", ["Device1","device2"]]}
{"SET_HC_MODE":["VENT", ["Device1","device2"]]}
```

VENT always available (fan without heat/cool). Target ≥36 disables cooling for that level; minimum cooling temp **18°C**.

#### neoStat HC-specific

```json
{"SET_COOL_TEMP":[27.5,"HCtest"]}
{"SET_FAN_SPEED":["HIGH",[...]]}
{"SET_FAN_SPEED":["AUTO",[...]]}
{"SET_FAN_SPEED":["MED",[...]]}
{"SET_FAN_SPEED":["LOW",[...]]}
{"SET_FAN_SPEED":["OFF",[...]]}
{"AUTO_MODE_OFF":["Device1", ...]}
```

In Vent mode, automatic fan control is disabled.

> **Warning:** neoStat HC does not use named profiles. Do not use `STORE_PROFILE` / `STORE_PROFILE2` — use `STORE_PROFILE_0`.

---

## Appendix A — Profiles

Worked examples of profile 0 and named profiles for each programmable mode and 4/6 levels.

### PROFILE 0 — 4 levels

**5/2 day:**

```json
{"STORE_PROFILE_0":[{
  "monday":{
    "leave":["09:00",16,127.5,true],
    "return":["16:00",21,127.5,true],
    "sleep":["22:00",16,127.5,true],
    "wake":["07:00",21,127.5,true]
  },
  "sunday":{
    "leave":["09:00",16,127.5,true],
    "return":["16:00",21,127.5,true],
    "sleep":["22:00",16,127.5,true],
    "wake":["07:00",21,127.5,true]
  }
},["Device Name"]]}
```

**24 hour:**

```json
{"STORE_PROFILE_0":[{
  "sunday":{
    "leave":["09:00",16,127.5,true],
    "return":["16:00",21,127.5,true],
    "sleep":["22:00",16,127.5,true],
    "wake":["07:00",21,127.5,true]
  }
},["Device Name"]]}
```

**7 day:** include `monday`–`sunday` (and `friday`, etc.) with the same four keys (`wake`/`leave`/`return`/`sleep`). See source PDF for the full literal payload.

### PROFILE 0 — 6 levels

Uses `wake`, `level1`–`level4`, `sleep` for each day key (`monday`/`sunday` for 5/2; `sunday` only for 24h; all weekdays for 7-day).

### Named profiles (`STORE_PROFILE`)

Same day/level shapes under `"info"`, plus `"name"`. Temperatures as floats with cooling fields, e.g. `["11:00",11.0, 25.0,true]`.

### Editing profiles

Load original → edit → store with `"ID": <existing>` so the profile ID is preserved and devices update.

### Default settings examples (Rev 3.2)

#### STORE_PROFILE_0 — 7 day (0.5° example)

```json
{
  "STORE_PROFILE_0": [{
    "friday": {
      "leave": ["09:15", 13.5, 0, false],
      "return": ["16:15", 21.5, 0, false],
      "sleep": ["22:15", 13.5, 0, false],
      "wake": ["07:15", 21.5, 0, false]
    },
    "monday": {
      "leave": ["09:15", 13.5, 0, false],
      "return": ["16:15", 21.5, 0, false],
      "sleep": ["22:15", 13.5, 0, false],
      "wake": ["07:15", 20.5, 0, false]
    },
    "saturday": {
      "leave": ["17:15", 13.5, 0, false],
      "return": ["21:15", 21.5, 0, false],
      "sleep": ["24:15", 13.5, 0, false],
      "wake": ["09:15", 21.5, 0, false]
    },
    "sunday": {
      "leave": ["16:15", 13.5, 0, false],
      "return": ["19:10", 21.5, 0, false],
      "sleep": ["23:05", 13.5, 0, false],
      "wake": ["09:15", 20.5, 0, false]
    },
    "thursday": {
      "leave": ["09:15", 13.5, 0, false],
      "return": ["16:15", 21.5, 0, false],
      "sleep": ["22:15", 13.5, 0, false],
      "wake": ["07:15", 21.5, 0, false]
    },
    "tuesday": {
      "leave": ["09:15", 13.5, 0, false],
      "return": ["16:15", 21.5, 0, false],
      "sleep": ["22:15", 13.5, 0, false],
      "wake": ["07:15", 21.5, 0, false]
    },
    "wednesday": {
      "leave": ["09:15", 13.5, 0, false],
      "return": ["16:15", 21.5, 0, false],
      "sleep": ["22:15", 13.5, 0, false],
      "wake": ["07:15", 21.5, 0, false]
    }
  }, "device name"]
}
```

#### STORE_PROFILE_0 — 5/2 day

Monday = weekdays; Sunday = weekend:

```json
{
  "STORE_PROFILE_0": [{
    "monday": {
      "leave": ["09:15", 13.5, 0, false],
      "return": ["16:15", 21.5, 0, false],
      "sleep": ["22:15", 13.5, 0, false],
      "wake": ["07:15", 20.5, 0, false]
    },
    "sunday": {
      "leave": ["16:15", 13.5, 0, false],
      "return": ["19:10", 21.5, 0, false],
      "sleep": ["23:05", 13.5, 0, false],
      "wake": ["09:15", 20.5, 0, false]
    }
  }, "device name"]
}
```

#### STORE_PROFILE_0 — 24 hour

```json
{
  "STORE_PROFILE_0": [{
    "sunday": {
      "leave": ["16:15", 13.5, 0, false],
      "return": ["19:10", 21.5, 0, false],
      "sleep": ["23:05", 13.5, 0, false],
      "wake": ["09:15", 20.5, 0, false]
    }
  }, "device name"]
}
```

#### STORE_PROFILE (named, 7-day shape)

```json
{
  "STORE_PROFILE": {
    "info": {
      "friday": {
        "leave": ["09:15", 13.5, 0, false],
        "return": ["16:15", 21.5, 0, false],
        "sleep": ["22:15", 13.5, 0, false],
        "wake": ["07:15", 21.5, 0, false]
      },
      "monday": {
        "leave": ["09:15", 13.5, 0, false],
        "return": ["16:15", 21.5, 0, false],
        "sleep": ["22:15", 13.5, 0, false],
        "wake": ["07:15", 20.5, 0, false]
      },
      "saturday": {
        "leave": ["17:15", 13.5, 0, false],
        "return": ["21:15", 21.5, 0, false],
        "sleep": ["24:15", 13.5, 0, false],
        "wake": ["09:15", 21.5, 0, false]
      },
      "sunday": {
        "leave": ["16:15", 13.5, 0, false],
        "return": ["19:10", 21.5, 0, false],
        "sleep": ["23:05", 13.5, 0, false],
        "wake": ["09:15", 20.5, 0, false]
      },
      "thursday": {
        "leave": ["09:15", 13.5, 0, false],
        "return": ["16:15", 21.5, 0, false],
        "sleep": ["22:15", 13.5, 0, false],
        "wake": ["07:15", 21.5, 0, false]
      },
      "tuesday": {
        "leave": ["09:15", 13.5, 0, false],
        "return": ["16:15", 21.5, 0, false],
        "sleep": ["22:15", 13.5, 0, false],
        "wake": ["07:15", 21.5, 0, false]
      },
      "wednesday": {
        "leave": ["09:15", 13.5, 0, false],
        "return": ["16:15", 21.5, 0, false],
        "sleep": ["22:15", 13.5, 0, false],
        "wake": ["07:15", 21.5, 0, false]
      }
    },
    "name": "profile name"
  }
}
```

#### Editing named profiles

1. `{"GET_PROFILE":"tested12"}` — note `PROFILE_ID`
2. Modify `info`
3. Re-store with matching ID semantics as documented above

---

## Appendix B — Deprecated commands

Still valid for backward compatibility; **do not use in new designs**:

```json
{"INFO":0}
{"ENGINEERS_DATA":0}
{"STORE_PROFILE":<profile ob>}
{"CLEAR_PROFILE":<profile name>}
{"GET_PROFILE":<profile name>}
{"RUN_PROFILE":<profile name>}
{"GET_PROFILE_NAMES":0}
```

Also deprecated elsewhere in the document: `READ_DCB`, `READ_COMFORT_LEVELS`, `SET_COMFORT_LEVELS`, `STATISTICS`.

---

## Appendix C — Alphabetical command list

| Command | Example | Notes |
| --- | --- | --- |
| AUTO_MODE_OFF | `{"AUTO_MODE_OFF":"HCtest"}` | HC fan auto off |
| AWAY_OFF | `{"AWAY_OFF":<device(s)>}` | |
| AWAY_ON | `{"AWAY_ON":<device(s)>}` | |
| BOOST_OFF | `{"BOOST_OFF":[{"hours":0,"minutes":10},<devices>]}` | |
| BOOST_ON | `{"BOOST_ON":[{"hours":0,"minutes":10},<devices>]}` | |
| CANCEL_HGROUP | `{"CANCEL_HGROUP":<group>}` | |
| CANCEL_HOLD_ALL | `{"CANCEL_HOLD_ALL":0}` | |
| CANCEL_HOLIDAY | `{"CANCEL_HOLIDAY":0}` | |
| CLEAR_CURRENT_PROFILE | `{"CLEAR_CURRENT_PROFILE":<devices>}` | |
| CLEAR_DEVICE_LIST | `{"CLEAR_DEVICE_LIST":<device>}` | |
| CLEAR_PROFILE | `{"CLEAR_PROFILE":<profile name>}` | Deprecated |
| CLEAR_PROFILE_ID | `{"CLEAR_PROFILE_ID":<number>}` | |
| CREATE_GROUP | `{"CREATE_GROUP":[[<devices>], <name>]}` | |
| DELETE_GROUP | `{"DELETE_GROUP":<group>}` | |
| DETACH_DEVICE | `{"DETACH_DEVICE":[<zone>,<device>]}` | |
| DEVICES_SN | `{"DEVICES_SN":0}` | |
| DST_OFF | `{"DST_OFF":0}` | |
| DST_ON | `{"DST_ON":0}` or `{"DST_ON":"UK"}` | See Appendix F |
| ENGINEERS_DATA | `{"ENGINEERS_DATA":0}` | Deprecated |
| SET_FAN_SPEED | `{"SET_FAN_SPEED":["HIGH",<device>]}` | Also AUTO, MED, LOW, OFF |
| FIRMWARE | `{"FIRMWARE":0}` | |
| FROST_OFF | `{"FROST_OFF":<device(s)>}` | |
| FROST_ON | `{"FROST_ON":<device(s)>}` | |
| GET_DEVICE_LIST | `{"GET_DEVICE_LIST":<device>}` | |
| GET_DEVICES | `{"GET_DEVICES":0}` | |
| GET_ENGINEERS | `{"GET_ENGINEERS":0}` | |
| GET_GROUPS | `{"GET_GROUPS":0}` | |
| GET_HOLD | `{"GET_HOLD":0}` | |
| GET_HOLIDAY | `{"GET_HOLIDAY":0}` | |
| GET_HOURSRUN | `{"GET_HOURSRUN":<device(s)>}` | |
| GET_LIVE_DATA | `{"GET_LIVE_DATA":0}` | |
| GET_PROFILE | `{"GET_PROFILE":<profile name>}` | Deprecated form |
| GET_PROFILE_0 | `{"GET_PROFILE_0":<devices>}` | |
| GET_PROFILE_NAMES | `{"GET_PROFILE_NAMES":0}` | Deprecated |
| GET_PROFILE_TIMERS | `{"GET_PROFILE_TIMERS":0}` | |
| GET_PROFILES | `{"GET_PROFILES":0}` | |
| GET_SYSTEM | `{"GET_SYSTEM":0}` | |
| GET_TEMPLOG | `{"GET_TEMPLOG":<device(s)>}` | |
| GET_TIMER_0 | `{"GET_TIMER_0":<device>}` | |
| GET_ZONES | `{"GET_ZONES":0}` | |
| GLOBAL_DEV_LIST | `{"GLOBAL_DEV_LIST":<devices>}` | |
| HOLD | `{"HOLD":[{"temp":<n>,"id":<s>,"hours":<n>,"minutes":<n>}, <device(s)>]}` | Also `cool` |
| HOLIDAY | `{"HOLIDAY":["HHMMSSDDMMYYYY","HHMMSSDDMMYYYY"]}` | |
| IDENTIFY | `{"IDENTIFY":0}` | |
| IDENTIFY_DEV | `{"IDENTIFY_DEV":<device>}` | |
| INFO | `{"INFO":0}` | Deprecated |
| LINK_DEVICE | `{"LINK_DEVICE":[<zone>,<device>]}` | |
| LOCK | `{"LOCK":[[<p1>,<p2>,<p3>,<p4>], <device(s)>]}` | |
| MANUAL_DST | `{"MANUAL_DST":<number>}` | |
| MANUAL_OFF | `{"MANUAL_OFF":<devices>}` | |
| MANUAL_ON | `{"MANUAL_ON":<devices>}` | |
| NTP_OFF | `{"NTP_OFF":0}` | |
| NTP_ON | `{"NTP_ON":0}` | |
| PERMIT_JOIN | `{"PERMIT_JOIN":[<seconds>,<device>]}` | Repeater: `["repeater", <seconds>]` |
| PROFILE_TITLE | `{"PROFILE_TITLE":[<old>,<new>]}` | |
| READ_COMFORT_LEVELS | `{"READ_COMFORT_LEVELS":<device(s)>}` | Deprecated |
| READ_DCB | `{"READ_DCB":100}` | Deprecated |
| READ_TIMECLOCK | `{"READ_TIMECLOCK":<device(s)>}` | |
| REMOVE_REPEATER | `{"REMOVE_REPEATER":<repeater>}` | |
| REMOVE_ZONE | `{"REMOVE_ZONE":<zone>}` | |
| RUN_PROFILE | `{"RUN_PROFILE":<profile name>}` | Deprecated |
| RUN_PROFILE_ID | `{"RUN_PROFILE_ID":[<profid>,<devices>]}` | |
| SET_CHANNEL | `{"SET_CHANNEL":<channel>}` | |
| SET_CLOSE_DELAY | `{"SET_CLOSE_DELAY":X}` | |
| SET_COMFORT_LEVELS | `{"SET_COMFORT_LEVELS":[<levels>, <device(s)>]}` | Deprecated |
| SET_COOL_TEMP | `{"SET_COOL_TEMP":[<temp>, <device(s)>]}` | |
| SET_DATE | `{"SET_DATE":[<year>, <month>, <day>]}` | |
| SET_DELAY | `{"SET_DELAY":[<delay>, <device(s)>]}` | |
| SET_DIFF | `{"SET_DIFF":[<diff>, <device(s)>]}` | |
| SET_FAILSAFE | `{"SET_FAILSAFE":[true\|false, 'neoair']}` | |
| SET_FLOOR | `{"SET_FLOOR":[<temp>, <device(s)>]}` | |
| SET_FORMAT | `{"SET_FORMAT":<format>}` | |
| SET_FROST | `{"SET_FROST":[<temp>, <device(s)>]}` | |
| SET_LEVEL_4 | `{"SET_LEVEL_4":0}` | |
| SET_LEVEL_6 | `{"SET_LEVEL_6":0}` | |
| SET_OPEN_DELAY | `{"SET_OPEN_DELAY":X}` | |
| SET_PREHEAT | `{"SET_PREHEAT":[<hours>, <device(s)>]}` | |
| SET_RF_MODE | `{"SET_RF_MODE":[<mode>, <devices>]}` | |
| SET_TEMP | `{"SET_TEMP":[<temp>, <device(s)>]}` | |
| SET_TEMP_FORMAT | `{"SET_TEMP_FORMAT":<format>}` | |
| SET_TIME | `{"SET_TIME":[<hours>,<minutes>]}` | |
| SET_TIMECLOCK | `{"SET_TIMECLOCK":[<levels>, <device(s)>]}` | |
| STATISTICS | `{"STATISTICS":0}` | Deprecated |
| STORE_PROFILE | `{"STORE_PROFILE":<profile ob>}` | Not for neoStat HC |
| STORE_PROFILE_0 | `{"STORE_PROFILE_0":[profile obj, devices]}` | |
| STORE_PROFILE_TIMER_0 | `{"STORE_PROFILE_TIMER_0":[profile obj, devices]}` | |
| SUMMER_OFF | `{"SUMMER_OFF":<device(s)>}` | |
| SUMMER_ON | `{"SUMMER_ON":<device(s)>}` | |
| TIME_ZONE | `{"TIME_ZONE":<timezone offset>}` | |
| TIMER_HOLD_OFF | `{"TIMER_HOLD_OFF":[<minutes>, <device(s)>]}` | |
| TIMER_HOLD_ON | `{"TIMER_HOLD_ON":[<minutes>, <device(s)>]}` | |
| TIMER_OFF | `{"TIMER_OFF":<device(s)>}` | |
| TIMER_ON | `{"TIMER_ON":<device(s)>}` | |
| UNLOCK | `{"UNLOCK":<device(s)>}` | |
| USER_LIMIT | `{"USER_LIMIT":[<int>, <device(s)>]}` | |
| VIEW_ROC | `{"VIEW_ROC":<device(s)>}` | |
| ZONE_TITLE | `{"ZONE_TITLE":[<oldname>, <newname>]}` | |

Additional commands documented in the body but not always listed in the PDF appendix table include: `RESET`, `GLOBAL_SYSTEM_TYPE`, `SET_GLOBAL_HC_MODE`, `SET_HC_MODE`, `STORE_RECIPE`, `RUN_RECIPE`, `DELETE_RECIPE`, `GET_RECIPES`, `STORE_PROFILE2`.

---

## Appendix D — Examples of cached files

### Get System

```json
{
  "ALT_TIMER_FORMAT": 2,
  "CORF": "C",
  "DEVICE_ID": "NeoHub",
  "DST_AUTO": false,
  "DST_ON": false,
  "FORMAT": 2,
  "HEATING_LEVELS": 4,
  "HEATORCOOL": "HeatOnly",
  "HUB_VERSION": 2081,
  "NTP_ON": " Running",
  "PARTITION": "4",
  "TIMESTAMP": 1518607836,
  "TIME_ZONE": 0,
  "UTC": 1519038792
}
```

### Live Data

See [Live data](#live-data). Devices may include `THERMOSTAT: true` or `TIMECLOCK: true`.

### Get Engineers / Get Profiles / Get Profile Timers

See earlier examples under engineers data and profiles. Sample named profile:

```json
{
  "ball": {
    "PROFILE_ID": 28,
    "group": null,
    "info": {
      "monday": {
        "leave": ["09:30",17],
        "return": ["17:30",25],
        "sleep": ["22:30",15],
        "wake": ["01:00",14]
      },
      "sunday": {
        "leave": ["09:30",17],
        "return": ["17:30",21],
        "sleep": ["22:30",15],
        "wake": ["01:00",21]
      }
    },
    "name": "ball"
  }
}
```

Timer profile sample:

```json
{
  "Timer": {
    "PROFILE_ID": 26,
    "group": null,
    "info": {
      "monday": {
        "time1": ["07:00","09:00"],
        "time2": ["16:00","20:00"],
        "time3": ["24:00","24:00"],
        "time4": ["24:00","24:00"]
      },
      "sunday": {
        "time1": ["07:00","09:00"],
        "time2": ["16:00","20:00"],
        "time3": ["24:00","24:00"],
        "time4": ["24:00","24:00"]
      }
    },
    "name": "Timer"
  }
}
```

---

## Appendix E — Neo System device type list

| Device | Type ID |
| --- | --- |
| TCM | 01 |
| Wi-Fi STAT / SMARTSTAT | 02 |
| COOLSWITCH | 03 |
| TCM-RH | 04 |
| WDS | 05 |
| NEOPLUG | 06 |
| NEOAIR | 07 |
| Smart Stat HC | 08 |
| NeoAir HW (combined) | 09 |
| REPEATER | 10 |
| NEOSTAT - HC | 11 |
| Neostat-V2 | 12 |
| Neoair V2 | 13 |
| Remote Air sensor | 14 |
| NeoAir-V2 combined mode | 15 |
| RF Switch Wifi | 16 |
| Edge wifi thermostat | 17 |

neoStat vs neoStat V2 (and neoAir V1 vs V2) use different IDs because of different hardware/firmware (relevant for hub firmware updates). JSON commands are unaffected.

For Generation 2 NeoHub from software **2112** onwards, read `"HUB_TYPE": 2` in the system cache.

---

## Appendix F — Daylight saving

Countries use different DST change dates; select the appropriate location.

Example: UK / most of Europe — last Sunday of March forward 1 hour; last Sunday of October back.

Original `{"DST_ON":0}` defaults to UK dates until the default is changed.

Read current setting: `"TIMEZONESTR": "UK"` in system cache.

To disable automatic DST:

```json
{"DST_OFF":0}
{"MANUAL_DST":0}
```

Example for New Zealand with NTP:

```json
{"NTP_ON":0}
{"TIME_ZONE":12}
{"DST_ON":"NZ"}
```

Available DST zones:

```json
{"DST_ON":"UK"}
{"DST_ON":"EU"}
{"DST_ON":"NZ"}
```

---

## Addendum

### Constant Fan

Keeps fans running when there is no call for heat or cooling (common in large buildings). `true`/`false` or `1`/`0`; corresponds to neoStat HC feature setting **12**. Location: engineers cache.

### Cool Proof

Delays fan start so water can warm up. Settings **00–95** seconds in **5**-second steps. Location: engineers cache.

### HUB_TYPE

| Type | Model |
| --- | --- |
| 1 | Original neoHub generation 1 |
| 2 | neoHub generation 2 with HomeKit |
| 3 | neoAir Hub |

---

*Converted from IMI Heatmiser neoHub API documentation. The [official PDF](https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf) remains the authoritative source for proprietary content and page-level references.*
