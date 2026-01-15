# Bitaxe HA Integration - Project Structure

```
bitaxe-ha/
├── .github/
│   └── workflows/
│       └── validate.yml              # GitHub Actions CI/CD workflow
├── .gitattributes                    # Git line ending rules
├── .gitignore                        # Git ignore rules
├── CONTRIBUTING.md                   # Contribution guidelines
├── INSTALLATION.md                   # Detailed installation guide
├── LICENSE                           # MIT License
├── README.md                         # Main documentation
├── hacs.json                         # HACS integration metadata
├── PROJECT_STRUCTURE.md              # This file
├── custom_components/
│   └── bitaxe/                      # Main integration code
│       ├── __init__.py              # Entry point, coordinator setup
│       ├── config_flow.py           # UI configuration flow
│       ├── const.py                 # Constants and configuration
│       ├── coordinator.py           # Data coordinator & periodic scanning
│       ├── discovery.py             # Network discovery logic
│       ├── manifest.json            # Integration manifest
│       ├── sensor.py                # Sensor entities
│       ├── strings.json             # UI text strings
│       └── translations/
│           └── en.json              # English translations
└── examples/
    └── automations.yaml             # Example automations
```

## File Descriptions

### Root Level

#### `.github/workflows/validate.yml`
GitHub Actions workflow for automated testing.
- **HACS validation**: Ensures HACS compatibility
- **Hassfest validation**: Home Assistant manifest validation
- **Ruff linting**: Code style and quality checks
- **Triggers**: On every push, PR, and daily schedule

#### `hacs.json`
HACS integration metadata:
- Defines integration name and domain
- Specifies Home Assistant minimum version
- Configures README rendering

#### `README.md`
Main user-facing documentation:
- Features overview
- Installation instructions (HACS & manual)
- Configuration guide
- Sensor descriptions
- Automation examples
- Dashboard examples
- Troubleshooting

#### `INSTALLATION.md`
Detailed step-by-step installation guide for different scenarios:
- HACS installation
- Manual installation
- Docker setup
- Home Assistant OS setup
- Network troubleshooting
- Verification steps

#### `CONTRIBUTING.md`
Guidelines for contributors:
- Development setup
- Testing procedures
- Code style requirements
- PR guidelines
- Issue templates

### Integration Code (`custom_components/bitaxe/`)

#### `__init__.py`
Entry point for the integration:
- **`async_setup_entry()`**: Creates coordinator, starts platforms
- **`async_unload_entry()`**: Cleanup on removal
- **Error handling**: Graceful failure with logging
- **Platform setup**: Delegates to platform files

#### `const.py`
Constants and configuration:
- Domain name (`bitaxe`)
- Default values (subnet, concurrency, timeout, intervals)
- Config flow keys for form data
- API endpoints and signatures
- Event names
- Device info (manufacturer, model)

#### `config_flow.py`
UI configuration flow using Voluptuous:
- **`async_step_user()`**: Initial setup form
  - Subnet validation (CIDR format)
  - Concurrency/timeout validation
  - Scan interval validation
- **`async_step_discovery()`**: Network scanning step
  - Initiates subnet discovery
  - Shows progress to user
- **`async_step_discovery_none()`**: Handles no miners found case
- **`async_step_select_miners()`**: Miner selection UI
  - Shows discovered miners as checkboxes
  - Requires at least one selection
  - Creates config entry with selected miners

#### `discovery.py`
Network discovery logic:
- **`BitaxeDiscovery` class**: Main discovery coordinator
  - Parses CIDR subnet
  - Creates concurrent probe tasks
  - Applies semaphore for concurrency limit
- **`_probe_ip()`**: Single IP probe
  - Checks for "NerdQAxe" signature in web interface
  - Verifies API endpoint is functional
  - Handles timeouts and connection errors
- **`_verify_bitaxe()`**: API verification
  - Confirms real Bitaxe by checking API endpoint
  - Validates expected JSON structure

#### `coordinator.py`
Data management and periodic operations:
- **`BitaxeCoordinator` class**: Main data coordinator
  - Extends Home Assistant's `DataUpdateCoordinator`
  - Manages periodic API polling (default: 30 seconds)
  - Tracks configured vs. active miners
  - Device registry integration
- **`_async_update_data()`**: Fetches miner data
  - Polls all active miners in parallel
  - Aggregates hashrate, temp, power, etc.
  - Handles missing miners gracefully
- **`_periodic_scan()`**: Background scanning task
  - Runs configurable interval scan (default: 1 hour, can be disabled)
  - Detects new miners (fires `bitaxe_miner_discovered` event)
  - Detects lost miners (fires `bitaxe_miner_lost` event)
  - Cancellable via `async_shutdown()`
- **Device registration**: Creates devices in Home Assistant device registry

#### `sensor.py`
Sensor entity definitions:
- **`BitaxeSensorEntityDescription`**: Data class for sensor metadata
  - `value_fn`: Lambda to extract value from miner data
  - `attr_fn`: Optional lambda for extra attributes
- **`SENSOR_TYPES`**: Tuple of all sensor definitions
  - Hashrate (H/s)
  - Uptime (seconds)
  - Temperature (°C)
  - Power (W)
  - Efficiency (J/GH)
  - ASIC count
- **`BitaxeSensor` class**: CoordinatorEntity implementation
  - Extends `CoordinatorEntity` for automatic updates
  - Creates unique IDs based on miner IP + sensor type
  - Registers devices in device registry
  - Handles unavailable state gracefully

#### `strings.json` & `translations/en.json`
UI text and localization:
- Config flow step descriptions
- Form field labels and help text
- Error messages
- Field validation messages
- Data descriptions for tooltips

#### `manifest.json`
Home Assistant integration manifest:
- `domain`: "bitaxe" (unique identifier)
- `name`: "Bitaxe" (display name)
- `icon`: "mdi:pickaxe" (Material Design icon)
- `config_flow`: true (supports UI configuration)
- `iot_class`: "local_polling" (local network, polling-based)
- `requirements`: ["aiohttp"] (Python dependencies)
- `homeassistant`: "2024.1.0" (minimum version)

### Examples

#### `examples/automations.yaml`
Ready-to-use automation examples:
- High temperature alerts
- Power consumption monitoring
- Miner discovery notifications
- Offline detection
- Daily/weekly reports
- Auto-restart on downtime
- Adaptive cooling

## Architecture

### Data Flow

```
Bitaxe Miner (HTTP API)
    |
    | /api/system/info
    | /api/system/metrics
    v
BitaxeCoordinator
    |
    ├─> Periodic polling (30s)
    ├─> Periodic discovery (1h, optional)
    │
    └─> Stores miner data
        |
        v
    Coordinator notifies listeners
        |
        v
    BitaxeSensor entities update
        |
        v
    Home Assistant state machine
```

### Component Relationships

```
ConfigFlow (User Configuration)
    |
    ├─> Discovery module (subnet scanning)
    |
    └─> Creates ConfigEntry

ConfigEntry
    |
    v
async_setup_entry (__init__.py)
    |
    ├─> Creates BitaxeCoordinator
    ├─> Starts periodic tasks
    └─> Sets up SENSOR platform

BitaxeCoordinator
    |
    ├─> Manages data ({ip: {stats}})
    ├─> Polls API periodically
    ├─> Periodic re-discovery
    └─> Device registry management

sensor.py (async_setup_entry)
    |
    ├─> Listens to coordinator updates
    ├─> Creates BitaxeSensor for each miner+type
    └─> Auto-adds new miners
```

## Key Design Decisions

### 1. Network Scanning Strategy
- **Initial scan** on setup (one-time)
- **Periodic scan** at configurable interval (default: disabled for efficiency)
- **Semaphore-limited** concurrency to avoid overwhelming network
- **Signature detection** (fast) before API verification (slow)

### 2. Data Polling vs. Discovery
- **Data polling**: Every 30 seconds (configurable)
- **Discovery scanning**: Every 3600 seconds / disabled (configurable)
- Separation allows frequent updates without expensive network scans

### 3. Async Architecture
- All network operations are fully async
- Uses `asyncio.gather()` for parallel requests
- `aiohttp.ClientSession` with proper timeout handling
- No blocking operations

### 4. Error Handling
- Gracefully handles unreachable miners (marks unavailable)
- Continues polling other miners if one fails
- Logs detailed debug info for troubleshooting
- Validates configuration early in config flow

### 5. Device Registry
- Each miner is a device with multiple sensors
- Proper device identifiers `(DOMAIN, miner_ip)`
- Persistent across restarts
- Allows grouping sensors by device

### 6. Config Entry Immutability
- Configuration stored in config entry
- Coordinator accesses via `entry.data`
- Changes require reconfiguration
- Clean separation of concerns

## Testing Checklist

- [ ] Install via manual copy
- [ ] Config flow accepts valid subnet (e.g., 192.168.1.0/24)
- [ ] Config flow rejects invalid subnet (e.g., 999.999.999.999/24)
- [ ] Discovery scan finds miners with correct signature
- [ ] Sensor entities created for each miner
- [ ] Sensors update with fresh data every 30 seconds
- [ ] Periodic scan (if enabled) discovers new miners
- [ ] Periodic scan detects lost miners
- [ ] Device registry has entries for all miners
- [ ] Integration unloads cleanly without errors
- [ ] Background tasks cancel on unload
- [ ] Logs are clear and helpful for debugging
- [ ] Ruff linting passes
- [ ] HACS validation passes
- [ ] Hassfest validation passes

## Deployment Paths

### To HACS Default Repository
1. Submit PR to [hacs/default](https://github.com/hacs/default)
2. Wait for review and approval
3. Integration becomes available in HACS

### As Custom Repository
1. Push to personal GitHub
2. Users add custom repository in HACS
3. Share URL: `https://github.com/YOUR_USERNAME/bitaxe-ha`

## Maintenance Tasks

### Version Updates
```bash
# Bump version in manifest.json
# Update README with changes
# Tag release
git tag v0.2.0
git push --tags
```

### Breaking Changes
- Update README migration guide
- Bump major version number
- Consider `config_flow.async_migrate_entry()` if needed

### Dependencies
- Monitor aiohttp for updates
- Home Assistant compatibility with new releases
- Python version support

## Performance Notes

- **Memory**: ~50-100 MB including data for 10+ miners
- **CPU**: Minimal impact (async operations, sleep between scans)
- **Network**: 
  - Discovery scan: ~100 KB per scan (depends on subnet size)
  - Data polling: ~1-2 KB per miner per poll
  - Total: ~100 KB/hour for 10 miners with discovery
  - Less than 10 KB/hour without periodic discovery

## Future Enhancements

- [ ] Add Climate entity for temperature monitoring/alerts
- [ ] Add Switch entity for power control
- [ ] Support for other mining devices (Antminer, etc.)
- [ ] Historical data storage/graphs
- [ ] Automatic firmware update checks
- [ ] Pool monitoring integration
- [ ] Multi-user authentication for API
- [ ] MQTT bridge for remote monitoring

## Resources

- [Home Assistant Integration Docs](https://developers.home-assistant.io/)
- [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [Entity Registry](https://developers.home-assistant.io/docs/entity_registry_index)
- [HACS Guidelines](https://hacs.xyz/docs/publish/start)
- [Bitaxe GitHub](https://github.com/skot/bitaxe)
