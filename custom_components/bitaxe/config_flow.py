"""Config flow for Bitaxe integration."""
from __future__ import annotations

import asyncio
import ipaddress
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_CONCURRENCY,
    CONF_MINERS,
    CONF_SCAN_INTERVAL,
    CONF_SUBNET,
    CONF_TIMEOUT,
    DEFAULT_CONCURRENCY,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SUBNET,
    DEFAULT_TIMEOUT,
    DOMAIN,
)
from .discovery import discover_miners

_LOGGER = logging.getLogger(__name__)


class InvalidSubnet(HomeAssistantError):
    """Error to indicate subnet is invalid."""


class DiscoveryFailed(HomeAssistantError):
    """Error to indicate discovery failed."""


class BitaxeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bitaxe."""

    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize."""
        super().__init__()
        self.discovered_miners: list[str] = []
        self.discovery_config: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate subnet
            try:
                ipaddress.IPv4Network(user_input[CONF_SUBNET], strict=False)
            except ValueError:
                errors[CONF_SUBNET] = "invalid_subnet"
            
            # Validate concurrency
            if not 1 <= user_input[CONF_CONCURRENCY] <= 100:
                errors[CONF_CONCURRENCY] = "invalid_concurrency"
            
            # Validate timeout
            if not 0.5 <= user_input[CONF_TIMEOUT] <= 10:
                errors[CONF_TIMEOUT] = "invalid_timeout"
            
            # Validate scan interval
            if user_input[CONF_SCAN_INTERVAL] < 0:
                errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"
            
            if not errors:
                # Store config for later steps
                self.discovery_config = user_input
                return await self.async_step_discovery()
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SUBNET, default=DEFAULT_SUBNET
                    ): str,
                    vol.Required(
                        CONF_CONCURRENCY, default=DEFAULT_CONCURRENCY
                    ): int,
                    vol.Required(
                        CONF_TIMEOUT, default=DEFAULT_TIMEOUT
                    ): vol.All(vol.Coerce(float)),
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): int,
                }
            ),
            errors=errors,
            description_placeholders={
                "subnet_example": DEFAULT_SUBNET,
            },
        )

    async def async_step_discovery(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Scan subnet for miners."""
        errors: dict[str, str] = {}
        
        if user_input is None:
            # Start discovery scan
            self.context["title_placeholders"] = {
                "subnet": self.discovery_config[CONF_SUBNET]
            }
            
            try:
                self.discovered_miners = await discover_miners(
                    subnet=self.discovery_config[CONF_SUBNET],
                    concurrency=self.discovery_config[CONF_CONCURRENCY],
                    timeout=self.discovery_config[CONF_TIMEOUT],
                )
                
                if not self.discovered_miners:
                    # No miners found, ask user if they want to proceed anyway
                    return await self.async_step_discovery_none()
                
                # Show list of discovered miners
                return await self.async_step_select_miners()
            
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.error("Discovery failed: %s", err)
                errors["base"] = "discovery_failed"
                return self.async_show_form(
                    step_id="discovery",
                    errors=errors,
                )
        
        # User triggered discovery again
        return self.async_show_form(
            step_id="discovery",
            description_placeholders={
                "subnet": self.discovery_config[CONF_SUBNET],
            },
        )

    async def async_step_discovery_none(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle case where no miners were discovered."""
        if user_input is not None:
            if user_input.get("continue"):
                return await self.async_step_select_miners()
            return await self.async_step_user()
        
        return self.async_show_form(
            step_id="discovery_none",
            description_placeholders={
                "subnet": self.discovery_config[CONF_SUBNET],
            },
        )

    async def async_step_select_miners(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select which miners to add."""
        if user_input is not None:
            selected_miners = user_input.get(CONF_MINERS, [])
            
            if not selected_miners:
                # Require at least one miner
                return self.async_show_form(
                    step_id="select_miners",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_MINERS): cv.multi_select(
                                {ip: ip for ip in self.discovered_miners}
                            ),
                        }
                    ),
                    errors={"base": "no_miners_selected"},
                    description_placeholders={
                        "subnet": self.discovery_config[CONF_SUBNET],
                        "count": str(len(self.discovered_miners)),
                    },
                )
            
            # Create entry with selected miners
            config_data = self.discovery_config.copy()
            config_data[CONF_MINERS] = selected_miners
            
            return self.async_create_entry(
                title=f"Bitaxe ({len(selected_miners)} miner{'s' if len(selected_miners) != 1 else ''})",
                data=config_data,
            )
        
        # Import cv for multi_select
        from homeassistant.helpers import config_validation as cv
        
        # Show list of discovered miners
        return self.async_show_form(
            step_id="select_miners",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MINERS): cv.multi_select(
                        {ip: ip for ip in self.discovered_miners}
                    ),
                }
            ),
            description_placeholders={
                "subnet": self.discovery_config[CONF_SUBNET],
                "count": str(len(self.discovered_miners)),
            },
        )
