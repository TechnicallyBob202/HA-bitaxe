# Bitaxe Home Assistant Integration

A proper Home Assistant custom integration for monitoring Rigol Bitaxe Bitcoin miners.

## Features

- 🔍 **Network Scanning** - Automatically discover Bitaxe miners on your subnet
- 🎛️ **UI Configuration** - Set up via Home Assistant UI (no YAML needed!)
- 🔄 **Real-time Monitoring** - Poll miner API for current stats
- 📊 **Comprehensive Sensors** - Hashrate, power, temperature, efficiency, and more
- 🏗️ **Proper Architecture** - Uses DataUpdateCoordinator, config entries, and modern HA patterns
- 🔁 **Periodic Re-discovery** - Optionally scan for new miners on a schedule
- 🎉 **Miner Events** - Get notified when miners are discovered or lost

## Installation

### HACS (Recommended - when published)

1. Open HACS
2. Go to Integrations
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add this repository URL
6. Install "Bitaxe"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/bitaxe` folder to your Home Assistant's `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Configuration → Integrations
4. Click "+ Add Integration"
5. Search for "Bitaxe"

## Configuration

1. After adding the integration, you'll be prompted for:
   - **Subnet**: The network subnet to scan (e.g., `192.168.1.0/24`)
   - **Concurrency**: Number of parallel probe connections (default: 20)
   - **Timeout**: Timeout per probe in seconds (default: 1.5)
   - **Scan Interval**: How often to re-scan for new miners in seconds (0 to disable)

2. Click "Next" to start discovery

3. The integration will scan your subnet and show you discovered miners

4. Select which miners you want to monitor and click "Submit"

5. Your miners will appear as devices and entities!

## Sensors

For each discovered miner (e.g., `192.168.1.105`), you get:

- `sensor.bitaxe_192_168_1_105_hashrate` - Current hashrate (H/s)
- `sensor.bitaxe_192_168_1_105_uptime` - Miner uptime (seconds)
- `sensor.bitaxe_192_168_1_105_temperature` - Device temperature (°C)
- `sensor.bitaxe_192_168_1_105_power_consumption` - Power draw (W)
- `sensor.bitaxe_192_168_1_105_efficiency` - J/GH (Joules per Gigahash)
- `sensor.bitaxe_192_168_1_105_asic_count` - Number of ASIC chips

## Events

### bitaxe_miner_discovered

Fired when a new miner is discovered during periodic scanning.

**Event Data:**
```python
{
    "miner_ip": "192.168.1.105",
}
```

### bitaxe_miner_lost

Fired when a previously seen miner is no longer found.

**Event Data:**
```python
{
    "miner_ip": "192.168.1.105",
}
```

## Automations

### Block Notification (when API supports it)

```yaml
automation:
  - alias: "Bitaxe - Block Found"
    trigger:
      - platform: event
        event_type: bitaxe_block_found
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "💎 Bitcoin Block Found!"
          message: >
            Miner {{ trigger.event.data.miner_ip }} found a block!
          data:
            priority: high
```

### High Temperature Alert

```yaml
automation:
  - alias: "Bitaxe - High Temperature"
    trigger:
      - platform: numeric_state
        entity_id:
          - sensor.bitaxe_192_168_1_105_temperature
          - sensor.bitaxe_192_168_1_106_temperature
        above: 60
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Miner Overheating"
          message: >
            {{ trigger.to_state.attributes.friendly_name }} is at {{ trigger.to_state.state }}°C
```

### Miner Discovered Alert

```yaml
automation:
  - alias: "Bitaxe - Miner Discovered"
    trigger:
      - platform: event
        event_type: bitaxe_miner_discovered
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "✅ New Miner Detected"
          message: "Miner {{ trigger.event.data.miner_ip }} is now being monitored"
```

### Offline Detection (using template sensor)

```yaml
template:
  - binary_sensor:
      - name: "Bitaxe Offline"
        unique_id: bitaxe_offline
        device_class: problem
        state: >
          {%- set offline = [] -%}
          {%- for state in states.sensor 
             if 'bitaxe' in state.entity_id 
             and 'hashrate' in state.entity_id 
             and state.state == 'unavailable' -%}
            {%- set offline = offline + [state.attributes.friendly_name] -%}
          {%- endfor -%}
          {{ offline|length > 0 }}
        attributes:
          offline_miners: >
            {%- set offline = [] -%}
            {%- for state in states.sensor 
               if 'bitaxe' in state.entity_id 
               and 'hashrate' in state.entity_id 
               and state.state == 'unavailable' -%}
              {%- set offline = offline + [state.attributes.friendly_name] -%}
            {%- endfor -%}
            {{ offline }}
```

## Template Sensors

### Total Hashrate

```yaml
template:
  - sensor:
      - name: "Total Bitaxe Hashrate"
        unique_id: bitaxe_total_hashrate
        unit_of_measurement: "GH/s"
        state_class: measurement
        state: >
          {% set ns = namespace(total=0.0) %}
          {% for state in states.sensor 
             if 'bitaxe' in state.entity_id 
             and 'hashrate' in state.entity_id 
             and state.state not in ['unknown', 'unavailable'] %}
            {% set ns.total = ns.total + (state.state | float(0)) %}
          {% endfor %}
          {{ (ns.total / 1000000000) | round(3) }}
        icon: mdi:chip
```

### Total Power Consumption

```yaml
template:
  - sensor:
      - name: "Total Bitaxe Power"
        unique_id: bitaxe_total_power
        unit_of_measurement: "W"
        state_class: measurement
        device_class: power
        state: >
          {% set ns = namespace(total=0.0) %}
          {% for state in states.sensor 
             if 'bitaxe' in state.entity_id 
             and 'power_consumption' in state.entity_id 
             and state.state not in ['unknown', 'unavailable'] %}
            {% set ns.total = ns.total + (state.state | float(0)) %}
          {% endfor %}
          {{ ns.total | round(2) }}
```

### Average Efficiency

```yaml
template:
  - sensor:
      - name: "Average Bitaxe Efficiency"
        unique_id: bitaxe_avg_efficiency
        unit_of_measurement: "J/GH"
        state_class: measurement
        state: >
          {% set ns = namespace(total=0.0, count=0) %}
          {% for state in states.sensor 
             if 'bitaxe' in state.entity_id 
             and 'efficiency' in state.entity_id 
             and state.state not in ['unknown', 'unavailable'] %}
            {% set ns.total = ns.total + (state.state | float(0)) %}
            {% set ns.count = ns.count + 1 %}
          {% endfor %}
          {{ (ns.total / ns.count) | round(2) if ns.count > 0 else 0 }}
```

## Dashboard Example

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      # ⛏️ Bitaxe Mining Operation
      **Total Hashrate:** {{ states('sensor.total_bitaxe_hashrate') }} GH/s
      **Total Power:** {{ states('sensor.total_bitaxe_power') }} W
      **Average Efficiency:** {{ states('sensor.average_bitaxe_efficiency') }} J/GH

  - type: entities
    title: "Miner Status"
    entities:
      - entity: sensor.bitaxe_192_168_1_105_hashrate
        name: "Miner 1 Hashrate"
      - entity: sensor.bitaxe_192_168_1_105_temperature
        name: "Miner 1 Temperature"
      - entity: sensor.bitaxe_192_168_1_105_power_consumption
        name: "Miner 1 Power"
      - entity: sensor.bitaxe_192_168_1_106_hashrate
        name: "Miner 2 Hashrate"
      - entity: sensor.bitaxe_192_168_1_106_temperature
        name: "Miner 2 Temperature"
      - entity: sensor.bitaxe_192_168_1_106_power_consumption
        name: "Miner 2 Power"

  - type: history-graph
    title: "Hashrate History (24h)"
    hours_to_show: 24
    entities:
      - sensor.bitaxe_192_168_1_105_hashrate
      - sensor.bitaxe_192_168_1_106_hashrate

  - type: history-graph
    title: "Temperature History (24h)"
    hours_to_show: 24
    entities:
      - sensor.bitaxe_192_168_1_105_temperature
      - sensor.bitaxe_192_168_1_106_temperature
```

## Troubleshooting

### Integration won't install
- Make sure you've restarted Home Assistant after copying files
- Check the logs for errors: Settings → System → Logs

### No miners appearing
1. **Verify subnet is correct:**
   - Check your network topology
   - Use `ping 192.168.1.1` to verify connectivity (adjust IP)

2. **Check firewall:**
   ```bash
   # If running on Linux, ensure HTTP is allowed
   sudo ufw allow http
   ```

3. **Verify Bitaxe web interface is accessible:**
   - Open browser to `http://YOUR_MINER_IP/`
   - Should see Bitaxe web UI

4. **Check scan logs:**
   - Settings → System → Logs
   - Look for "Bitaxe" entries
   - Increase log level for debugging

### Sensors show "unavailable"
- Wait 30 seconds for first data fetch
- Check miner is online: `ping MINER_IP`
- Check Home Assistant logs for errors
- Ensure miner's API endpoint is responding: `curl http://MINER_IP/api/system/info`

### Reinstalling the integration
1. Settings → Integrations → Bitaxe → Delete
2. Delete `custom_components/bitaxe` directory
3. Restart Home Assistant
4. Re-add the integration

## API Endpoints Used

The integration expects the following API endpoints on Bitaxe miners:

- `GET /` - Web interface (for discovery signature detection)
- `GET /api/system/info` - System information
- `GET /api/system/metrics` - Runtime metrics/stats

If your Bitaxe firmware doesn't support these endpoints, please check the firmware version.

## Technical Details

### Architecture
- **Discovery**: Subnet scanning with configurable concurrency and timeout
- **Data Collection**: HTTP API polling with DataUpdateCoordinator
- **Updates**: Periodic polling (default 30 seconds) + periodic re-discovery
- **Device Registry**: Proper device and entity registry integration

### Scanning Strategy
1. **Startup**: One-time full subnet scan on integration load
2. **Periodic**: Optional re-scan at configurable interval (default: disabled)
3. **Manual**: User can re-run discovery from UI

### Network Efficiency
- Async concurrent probing (configurable concurrency limit)
- Per-host timeout to avoid hanging
- Signature detection (fast) before full verification (slower)

## Support

- **Bitaxe Firmware**: https://github.com/skot/bitaxe
- **Home Assistant Community**: https://community.home-assistant.io/

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests or open issues on GitHub.

## Changelog

### Version 0.1.0 (Initial Release)
- Network discovery scanning
- Sensor entities for hashrate, temperature, power, efficiency
- Event notifications for miner discovery/loss
- Periodic re-discovery support
- Full Home Assistant integration architecture
