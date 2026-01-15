"""Constants for the Bitaxe integration."""
from typing import Final

DOMAIN: Final = "bitaxe"

# Default configuration values
DEFAULT_SUBNET: Final = "192.168.1.0/24"
DEFAULT_CONCURRENCY: Final = 20
DEFAULT_TIMEOUT: Final = 1.5
DEFAULT_SCAN_INTERVAL: Final = 3600  # 1 hour
DEFAULT_POLL_INTERVAL: Final = 30  # 30 seconds

# Config flow keys
CONF_SUBNET: Final = "subnet"
CONF_CONCURRENCY: Final = "concurrency"
CONF_TIMEOUT: Final = "timeout"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_POLL_INTERVAL: Final = "poll_interval"
CONF_MINERS: Final = "miners"  # List of manually added miner IPs

# Discovery
DISCOVERY_SIGNATURE: Final = "NerdQAxe"
DISCOVERY_ENDPOINT: Final = "/"
API_INFO_ENDPOINT: Final = "/api/system/info"
API_STATS_ENDPOINT: Final = "/api/system/metrics"

# Update intervals
SCAN_INTERVAL: Final = DEFAULT_SCAN_INTERVAL
POLL_INTERVAL: Final = DEFAULT_POLL_INTERVAL

# Platforms
PLATFORMS: Final = ["sensor"]

# Events
EVENT_MINER_DISCOVERED: Final = "bitaxe_miner_discovered"
EVENT_MINER_LOST: Final = "bitaxe_miner_lost"

# Device info
MANUFACTURER: Final = "Rigol"
MODEL_BITAXE: Final = "BitAxe"
