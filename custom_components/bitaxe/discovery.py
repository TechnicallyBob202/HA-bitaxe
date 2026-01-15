"""Network discovery for Bitaxe miners."""
from __future__ import annotations

import asyncio
import ipaddress
import logging
from typing import Any

import aiohttp

from .const import (
    API_INFO_ENDPOINT,
    DISCOVERY_ENDPOINT,
    DISCOVERY_SIGNATURE,
)

_LOGGER = logging.getLogger(__name__)


class BitaxeDiscovery:
    """Scan subnet for Bitaxe miners."""

    def __init__(
        self,
        subnet: str,
        concurrency: int = 20,
        timeout: float = 1.5,
    ) -> None:
        """Initialize discovery."""
        self.subnet = subnet
        self.concurrency = concurrency
        self.timeout = timeout
        self.sem = asyncio.Semaphore(concurrency)

    async def discover(self) -> list[str]:
        """Scan subnet for Bitaxe miners.
        
        Returns list of IPs of discovered miners.
        """
        _LOGGER.info(
            "Starting discovery scan: subnet=%s, concurrency=%s, timeout=%s",
            self.subnet,
            self.concurrency,
            self.timeout,
        )
        
        try:
            network = ipaddress.IPv4Network(self.subnet, strict=False)
        except ValueError as err:
            _LOGGER.error("Invalid subnet format: %s", err)
            return []
        
        # Create probe task for each IP
        tasks = [self._probe_ip(str(ip)) for ip in network.hosts()]
        
        # Gather all results (ignore exceptions)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None values and exceptions
        found_miners = [ip for ip in results if isinstance(ip, str)]
        
        _LOGGER.info("Discovery complete: found %d miner(s)", len(found_miners))
        return found_miners

    async def _probe_ip(self, ip: str) -> str | None:
        """Probe single IP for Bitaxe miner.
        
        Returns IP if miner found, None otherwise.
        """
        async with self.sem:
            try:
                url = f"http://{ip}{DISCOVERY_ENDPOINT}"
                
                # Use shorter timeout for initial discovery
                timeout = aiohttp.ClientTimeout(
                    total=self.timeout,
                    connect=self.timeout / 2,
                    sock_read=self.timeout / 2,
                )
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, allow_redirects=False) as response:
                        # Don't need to read full content, just check signature
                        # BitAxe web interface should contain "NerdQAxe" or similar
                        text = await response.text(errors="ignore")
                        
                        if DISCOVERY_SIGNATURE in text:
                            _LOGGER.debug("Found miner at %s", ip)
                            
                            # Verify it's actually a Bitaxe by checking API endpoint
                            if await self._verify_bitaxe(ip):
                                return ip
                        
            except asyncio.TimeoutError:
                # Expected for non-responsive hosts
                pass
            except aiohttp.ClientError as err:
                _LOGGER.debug("Connection error to %s: %s", ip, type(err).__name__)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.debug("Unexpected error probing %s: %s", ip, err)
            
            return None

    async def _verify_bitaxe(self, ip: str) -> bool:
        """Verify that IP is actually a Bitaxe by checking API."""
        try:
            url = f"http://{ip}{API_INFO_ENDPOINT}"
            
            timeout = aiohttp.ClientTimeout(
                total=self.timeout,
                connect=self.timeout / 2,
            )
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Basic validation - should have expected fields
                        if "version" in data or "uptime" in data:
                            _LOGGER.debug("Verified Bitaxe at %s", ip)
                            return True
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.debug("Could not verify API at %s: %s", ip, err)
        
        return False


async def discover_miners(
    subnet: str,
    concurrency: int = 20,
    timeout: float = 1.5,
) -> list[str]:
    """Convenience function for discovery."""
    discovery = BitaxeDiscovery(subnet, concurrency, timeout)
    return await discovery.discover()
