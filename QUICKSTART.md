# Bitaxe Integration - Quick Start

## What Was Built

A complete Home Assistant integration for monitoring Rigol Bitaxe Bitcoin miners via their HTTP API.

## Key Differences from NMMiner

| Aspect | NMMiner | Bitaxe |
|--------|---------|--------|
| **Protocol** | UDP broadcasts (push) | HTTP API (pull/polling) |
| **Discovery** | None (waits for broadcasts) | Network scanning (active) |
| **Updates** | Event-driven (5s) | Polling interval (30s default) |
| **Scan Type** | N/A | Configurable periodic scans |

## Architecture

```
User Config → Discovery Scan → Select Miners → Polling Loop
                                              ↓
                                         Periodic Scan
                                              ↓
                                         Device Registry
                                              ↓
                                         Home Assistant
```

## Features Implemented

✅ **Network Discovery**
- Async concurrent subnet scanning
- API verification
- Configurable timeout and concurrency

✅ **Configuration Flow**
- Subnet CIDR input
- Scan settings (concurrency, timeout)
- Miner selection
- Periodic scan interval configuration

✅ **Data Coordination**
- Periodic API polling (30s intervals)
- Parallel miner data fetches
- Device registry integration
- Error handling for offline miners

✅ **Sensor Entities** (25 sensors per miner)
- Mining stats (hashrate, shares, difficulty, blocks)
- Temperature monitoring (device, VR)
- Power & voltage (consumption, core voltage)
- Cooling (fan speed, RPM, manual override)
- System (uptime, frequency, ASIC count, efficiency)
- Network (WiFi signal, pool ping latency/loss, SSID)
- Device info (model, connection status)

✅ **Events**
- `bitaxe_miner_discovered` - When new miner found
- `bitaxe_miner_lost` - When miner goes offline

✅ **Periodic Re-discovery**
- Optional background scanning
- Configurable interval (0 = disabled)
- Auto-detects new/missing miners

## Quick Development Guide

### Testing Locally

```bash
# Copy to Home Assistant
cp -r custom_components/bitaxe ~/.homeassistant/custom_components/

# Restart HA
# Then add via Settings → Devices & Services
```

### Key Files to Modify

1. **`discovery.py`** - Change miner detection logic
2. **`coordinator.py`** - Modify polling interval or data fetching
3. **`sensor.py`** - Add/modify sensor types
4. **`const.py`** - Change constants and defaults

### Adding New Sensors

```python
# In sensor.py, add to SENSOR_TYPES tuple:

BitaxeSensorEntityDescription(
    key="my_sensor",
    name="My Sensor Name",
    native_unit_of_measurement="unit",
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:icon-name",
    value_fn=lambda data: data.get("api_field", 0),
),
```

Example from actual integration:
```python
BitaxeSensorEntityDescription(
    key="pool_ping_rtt",
    name="Pool Ping RTT",
    native_unit_of_measurement="ms",
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:ping",
    value_fn=lambda data: data.get("lastpingrtt", 0),
),
```

### Changing Discovery Logic

```python
# In discovery.py, modify _probe_ip():
# - Change API_INFO_ENDPOINT constant
# - Modify logic to check different fields
# - Adjust timeout or connection logic
```

## Configuration Schema

```yaml
bitaxe:
  subnet: "192.168.1.0/24"     # Network to scan
  concurrency: 20              # Parallel probes
  timeout: 1.5                 # Seconds per probe
  scan_interval: 3600          # Seconds between scans (0=disabled)
  poll_interval: 30            # Seconds between data polls
```

## API Endpoints Assumed

```
GET /api/system/info           # System information
GET /api/system/metrics        # Runtime metrics/stats
```

If your Bitaxe firmware has different endpoints, modify in `const.py`.

## Next Steps

1. **Test with actual miners**
   - Verify API endpoints return expected JSON
   - Adjust API response parsing if needed

2. **Expand sensor types**
   - Add more fields based on API responses
   - Create template sensors for aggregation

3. **Add automations**
   - Use block detection for notifications
   - Monitor temperature/efficiency
   - Use events for miner discovery/loss

4. **Publish to HACS**
   - Update GitHub repo URL in files
   - Submit PR to HACS default repository

## File Structure Reference

```
bitaxe-ha/
├── custom_components/bitaxe/
│   ├── __init__.py          ← Entry point
│   ├── config_flow.py       ← UI configuration
│   ├── coordinator.py       ← Data management + polling
│   ├── discovery.py         ← Network scanning
│   ├── sensor.py            ← Sensor entities (25 sensors)
│   ├── const.py             ← Constants
│   └── manifest.json        ← Integration metadata
├── README.md                ← User documentation
├── INSTALLATION.md          ← Setup guide
├── CONTRIBUTING.md          ← Dev guide
├── QUICKSTART.md            ← This file
└── PROJECT_STRUCTURE.md     ← Detailed architecture
```

## Common Customizations

### Change Polling Interval
```python
# In const.py
DEFAULT_POLL_INTERVAL: Final = 60  # Changed from 30
```

### Change Default Subnet
```python
# In const.py
DEFAULT_SUBNET: Final = "10.0.0.0/24"  # Changed from 192.168.1.0/24
```

### Disable Periodic Scanning
```python
# In const.py
DEFAULT_SCAN_INTERVAL: Final = 0  # 0 = disabled
```

### Change Timeout
```python
# In const.py
DEFAULT_TIMEOUT: Final = 2.0  # Seconds per probe (was 1.5)
```

## Debugging Tips

### Check Discovery Logs
```yaml
# Add to configuration.yaml
logger:
  logs:
    custom_components.bitaxe: debug
```

### Verify API Endpoint
```bash
# From HA host
curl http://MINER_IP/api/system/info
curl http://MINER_IP/api/system/metrics
```

### Monitor Coordinator Data
- Settings → Developer Tools → States
- Search for `sensor.bitaxe_*`
- Check state and attributes

## Performance Expectations

- **Memory**: ~50-100 MB for 10+ miners
- **CPU**: Minimal (async only)
- **Network**: ~10 KB/hour data + discovery scans
- **Startup**: ~30 seconds to first sensor update
- **Re-scan time**: ~10 seconds for /24 subnet

## Troubleshooting

**Miners not found?**
- Check subnet format: `192.168.1.0/24` (CIDR)
- Verify miner IP is in subnet
- Test: `curl http://MINER_IP/api/system/info`

**Sensors unavailable?**
- Wait 30+ seconds for first poll
- Check API endpoints are accessible
- Review Home Assistant logs

**High CPU during scan?**
- Reduce concurrency (default: 20)
- Increase timeout (default: 1.5s)

**Integration won't load?**
- Check manifest.json syntax
- Review Home Assistant logs
- Verify all imports in Python files

---

Ready to customize? Start with `sensor.py` to add new sensors or `discovery.py` to adapt to your specific Bitaxe firmware! 🚀