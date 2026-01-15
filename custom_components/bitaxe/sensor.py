"""Sensor platform for Bitaxe integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BitaxeCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class BitaxeSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass
class BitaxeSensorEntityDescription(
    SensorEntityDescription, BitaxeSensorEntityDescriptionMixin
):
    """Describes Bitaxe sensor entity."""

    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def _calculate_efficiency(data: dict[str, Any]) -> float:
    """Calculate J/GH from power and hashrate."""
    try:
        power = data.get("power", 0)
        hashrate = data.get("hashRate", 0)
        
        if hashrate > 0:
            # Efficiency = Power (W) / Hashrate (GH/s)
            # hashRate is in H/s, need to convert to GH/s
            hashrate_gh = hashrate / 1_000_000_000
            efficiency = power / hashrate_gh
            return round(efficiency, 2)
    except (ValueError, ZeroDivisionError):
        pass
    return 0


# Sensor descriptions
SENSOR_TYPES: tuple[BitaxeSensorEntityDescription, ...] = (
    BitaxeSensorEntityDescription(
        key="hashrate",
        name="Hashrate",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chip",
        value_fn=lambda data: data.get("hashRate", 0),
    ),
    BitaxeSensorEntityDescription(
        key="uptime",
        name="Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("uptimeSeconds", 0),
    ),
    BitaxeSensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("temp", 0),
    ),
    BitaxeSensorEntityDescription(
        key="power",
        name="Power Consumption",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("power", 0),
    ),
    BitaxeSensorEntityDescription(
        key="efficiency",
        name="Efficiency",
        native_unit_of_measurement="J/GH",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:leaf",
        value_fn=lambda data: _calculate_efficiency(data),
    ),
    BitaxeSensorEntityDescription(
        key="asic_count",
        name="ASIC Count",
        icon="mdi:chip",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("asicCount", 0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bitaxe sensor based on a config entry."""
    coordinator: BitaxeCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Track which miners we've created entities for
    created_miners: set[str] = set()

    @callback
    def async_add_miner_sensors() -> None:
        """Add sensors for miners."""
        new_entities: list[BitaxeSensor] = []
        
        if not coordinator.data:
            return
        
        for miner_ip in coordinator.active_miners:
            if miner_ip not in created_miners:
                _LOGGER.info("Creating sensors for miner %s", miner_ip)
                created_miners.add(miner_ip)
                
                for description in SENSOR_TYPES:
                    new_entities.append(
                        BitaxeSensor(coordinator, miner_ip, description)
                    )
        
        if new_entities:
            async_add_entities(new_entities)

    # Listen for new miners
    coordinator.async_add_listener(async_add_miner_sensors)
    
    # Add any existing miners
    async_add_miner_sensors()


class BitaxeSensor(CoordinatorEntity[BitaxeCoordinator], SensorEntity):
    """Representation of a Bitaxe sensor."""

    entity_description: BitaxeSensorEntityDescription

    def __init__(
        self,
        coordinator: BitaxeCoordinator,
        miner_ip: str,
        description: BitaxeSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._miner_ip = miner_ip
        
        # Entity ID - replace dots with underscores
        safe_ip = miner_ip.replace(".", "_")
        self._attr_unique_id = f"bitaxe_{safe_ip}_{description.key}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, miner_ip)},
            "name": f"Bitaxe {miner_ip}",
        }
        
        # Entity name
        self._attr_name = f"Bitaxe {miner_ip} {description.name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self._miner_ip not in self.coordinator.miners:
            return False
        
        data = self.coordinator.miners[self._miner_ip]
        return data.get("available", True)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self._miner_ip not in self.coordinator.miners:
            return None
        
        data = self.coordinator.miners[self._miner_ip]
        
        if not data.get("available", True):
            return None
        
        return self.entity_description.value_fn(data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self._miner_ip not in self.coordinator.miners:
            return None
        
        if self.entity_description.attr_fn is None:
            return None
        
        data = self.coordinator.miners[self._miner_ip]
        return self.entity_description.attr_fn(data)