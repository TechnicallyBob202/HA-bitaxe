# Installation Guide - Bitaxe Home Assistant Integration

## Quick Install via HACS (Recommended)

### Prerequisites
- Home Assistant 2024.1.0 or newer
- HACS installed and configured

### Steps

1. **Open HACS**
   - Go to HACS in your Home Assistant sidebar

2. **Add Custom Repository** (if not in default HACS)
   - Click the three dots (⋮) in the top right
   - Select "Custom repositories"
   - Repository: `https://github.com/YOUR_USERNAME/bitaxe-ha`
   - Category: Integration
   - Click "Add"

3. **Install Integration**
   - Click "+ Explore & Download Repositories"
   - Search for "Bitaxe"
   - Click "Bitaxe"
   - Click "Download"
   - Select the latest version
   - Click "Download"

4. **Restart Home Assistant**
   - Settings → System → Restart Home Assistant

5. **Add Integration**
   - Settings → Devices & Services
   - Click "+ Create Automation" → "+ Add Integration"
   - Search for "Bitaxe"
   - Configure subnet and scan settings
   - Select miners to monitor
   - Click "Submit"

6. **Done!**
   - Your miners should appear within 30 seconds

---

## Manual Installation

### Prerequisites
- SSH access to your Home Assistant instance
- Home Assistant 2024.1.0 or newer

### Steps

1. **Download the Integration**
   ```bash
   cd /tmp
   git clone https://github.com/YOUR_USERNAME/bitaxe-ha
   cd bitaxe-ha
   ```

2. **Copy to Home Assistant**
   ```bash
   cp -r custom_components/bitaxe /config/custom_components/
   ```
   
   If using SSH:
   ```bash
   scp -r custom_components/bitaxe user@homeassistant.local:/config/custom_components/
   ```

3. **Set Permissions**
   ```bash
   chmod -R 755 /config/custom_components/bitaxe
   ```

4. **Verify Installation**
   ```bash
   ls -la /config/custom_components/bitaxe/
   ```
   
   You should see:
   ```
   __init__.py
   config_flow.py
   const.py
   coordinator.py
   discovery.py
   manifest.json
   sensor.py
   strings.json
   translations/
   ```

5. **Restart Home Assistant**
   - Settings → System → Restart Home Assistant

6. **Add Integration**
   - Settings → Devices & Services
   - Click "+ Create Automation" → "+ Add Integration"
   - Search for "Bitaxe"
   - Complete the configuration wizard

---

## Docker Installation

If running Home Assistant in Docker:

### Docker Compose

```yaml
version: '3.8'
services:
  homeassistant:
    container_name: homeassistant
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
    network_mode: host  # Required for network scanning to work
    restart: unless-stopped
```

Then copy the integration:
```bash
cp -r custom_components/bitaxe ./config/custom_components/
docker-compose restart homeassistant
```

### Docker Run

```bash
docker run -d \
  --name homeassistant \
  --privileged \
  --restart unless-stopped \
  -e TZ=UTC \
  -v /path/to/config:/config \
  --network host \
  homeassistant/home-assistant:latest
```

**Important:** Use `--network host` so Home Assistant can scan your local network.

---

## Home Assistant OS Installation

### Via Terminal Add-on

1. **Install Terminal & SSH Add-on**
   - Settings → Add-ons → Add-on Store
   - Search for "Terminal & SSH"
   - Install and start

2. **Connect via SSH**
   ```bash
   ssh root@homeassistant.local
   ```

3. **Download and Install**
   ```bash
   cd /tmp
   git clone https://github.com/YOUR_USERNAME/bitaxe-ha
   cp -r bitaxe-ha/custom_components/bitaxe /config/custom_components/
   ```

4. **Restart Home Assistant**
   - Settings → System → Restart Home Assistant

---

## Home Assistant Supervised (Docker)

```bash
# SSH into host
ssh root@host

# Navigate to config
cd /usr/share/hassio/homeassistant

# Clone and copy
git clone https://github.com/YOUR_USERNAME/bitaxe-ha /tmp/bitaxe-ha
cp -r /tmp/bitaxe-ha/custom_components/bitaxe ./custom_components/

# Restart container
docker restart homeassistant
```

---

## Verification

### Check Installation

1. **Verify Files Exist**
   ```bash
   ls -la /config/custom_components/bitaxe/
   ```

2. **Check Home Assistant Logs**
   - Settings → System → Logs
   - Restart Home Assistant
   - Look for any errors

3. **Verify Integration Appears**
   - Settings → Devices & Services
   - You should see "Bitaxe" in the integrations list

### Test Discovery

1. **Check Network Connectivity**
   ```bash
   # From HA host
   ping 192.168.1.1  # Your network gateway
   ```

2. **Test Miner Accessibility**
   ```bash
   # From HA host
   curl http://192.168.1.105/  # Your miner IP
   # Should see HTML with "NerdQAxe" somewhere
   ```

3. **Check HA Logs During Discovery**
   - Settings → System → Logs
   - Look for lines like: "Starting discovery scan"
   - Look for: "Found X miner(s)"

---

## Troubleshooting

### Integration Not Showing

```bash
# Check file permissions
chmod -R 755 /config/custom_components/bitaxe/

# Check manifest
cat /config/custom_components/bitaxe/manifest.json

# Check logs
tail -f /config/home-assistant.log | grep -i bitaxe
```

### Discovery Not Finding Miners

1. **Verify Subnet is Correct**
   ```bash
   # Check your IP
   ip addr show
   # Your HA should be in 192.168.x.x range
   ```

2. **Check Miner is Online**
   ```bash
   ping 192.168.1.105  # Your miner IP
   ```

3. **Test API Endpoint**
   ```bash
   # From HA host
   curl http://192.168.1.105/api/system/info
   # Should return JSON
   ```

4. **Enable Debug Logging**
   ```yaml
   # Add to configuration.yaml
   logger:
     default: info
     logs:
       custom_components.bitaxe: debug
   ```
   
   Then restart and check logs.

5. **Check Firewall**
   ```bash
   # If using UFW
   sudo ufw allow 8123/tcp  # HA port
   sudo ufw allow from 192.168.1.0/24 to any port 80  # HTTP
   ```

### Sensors Unavailable

1. **Wait for First Update**
   - Data is fetched every 30 seconds
   - Wait at least 60 seconds after adding integration

2. **Verify API Responses**
   ```bash
   # Test info endpoint
   curl http://192.168.1.105/api/system/info
   
   # Test metrics endpoint
   curl http://192.168.1.105/api/system/metrics
   ```

3. **Check Miner Firmware**
   - Open http://192.168.1.105/ in browser
   - Look for firmware version
   - Ensure it supports `/api/system/info` and `/api/system/metrics`

### High CPU Usage During Scan

1. **Reduce Concurrency**
   - Settings → Integrations → Bitaxe → Options
   - Reduce "Concurrent Scans" (default: 20)
   - Try 5-10 if scanning large networks

2. **Increase Timeout**
   - Increase "Probe Timeout" (default: 1.5s)
   - Try 2-3 seconds for slower networks

### Network Issues

#### Miners on Different VLAN
```bash
# Configure static route
# From HA host
ip route add 192.168.10.0/24 via 192.168.1.1

# Or configure on gateway/router
# Enable VLAN routing and ensure broadcasts are allowed
```

#### Behind VPN/Proxy
```bash
# Add firewall rule to allow local network broadcasts
# This is very router/VPN dependent
# Consult your network documentation
```

---

## Updating

### Via HACS
1. Go to HACS → Integrations
2. Find "Bitaxe"
3. Click "Update" if available
4. Restart Home Assistant

### Manual Update
1. Download latest version
2. Replace files in `/config/custom_components/bitaxe/`
3. Restart Home Assistant
4. Check changelog for breaking changes

---

## Uninstalling

### Remove Integration
1. Settings → Devices & Services
2. Find "Bitaxe"
3. Click three dots (⋮)
4. Select "Delete"
5. Confirm deletion

### Remove Files
```bash
rm -rf /config/custom_components/bitaxe
```

### Restart
- Settings → System → Restart Home Assistant

---

## Getting Help

- **GitHub Issues**: https://github.com/YOUR_USERNAME/bitaxe-ha/issues
- **Home Assistant Docs**: https://developers.home-assistant.io/
- **Bitaxe Community**: https://github.com/skot/bitaxe
- **HA Community Forum**: https://community.home-assistant.io/

## System Requirements

| Component | Requirement |
|-----------|------------|
| Home Assistant | 2024.1.0+ |
| Python | 3.11+ |
| Network | Local network access to miners |
| Memory | 50-100 MB for the integration |
| CPU | Minimal impact (async operations) |

## Optional Improvements

### Increase Log Level for Debugging
```yaml
# configuration.yaml
logger:
  logs:
    custom_components.bitaxe: debug
    aiohttp: debug
```

### Monitor Integration Health
```yaml
# Template binary sensor for offline detection
template:
  - binary_sensor:
      - name: "Bitaxe Unhealthy"
        unique_id: bitaxe_health
        device_class: problem
        state: >
          {{ states.sensor | selectattr('entity_id', 'search', 'bitaxe')
             | map(attribute='state')
             | select('eq', 'unavailable')
             | list | length > 0 }}
```

---

Good luck with your Bitaxe mining operation! 🚀⛏️
