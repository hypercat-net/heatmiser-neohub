"""IMI Heatmiser NeoHub client library."""

from heatmiser_neohub.client import NeoHubClient, NeoHubError, NeoHubTimeoutError
from heatmiser_neohub.discover import (
    DiscoveredHub,
    DiscoveryError,
    discover_hubs,
    resolve_hub_host,
    resolve_hub_port,
)
from heatmiser_neohub.models import Device, LiveData, SystemInfo

__all__ = [
    "Device",
    "DiscoveredHub",
    "DiscoveryError",
    "LiveData",
    "NeoHubClient",
    "NeoHubError",
    "NeoHubTimeoutError",
    "SystemInfo",
    "discover_hubs",
    "resolve_hub_host",
    "resolve_hub_port",
]

__version__ = "1.0.0"
