"""DataUpdateCoordinator voor Strand & Zee."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import fetch_open_meteo
from .const import CONF_LATITUDE, CONF_LONGITUDE, DOMAIN, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)

QUANTITIES = (
    "water_temperature",
    "wave_height",
    "wave_period",
    "wind_speed",
    "wind_direction",
)


@dataclass
class Reading:
    """Eén meetwaarde."""

    value: float
    timestamp: datetime


class StrandEnZeeCoordinator(DataUpdateCoordinator[dict[str, Reading | None]]):
    """Haalt de huidige zee- en windwaarden op voor één strand of plas."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )
        self._session = async_get_clientsession(hass)
        self._lat = entry.data[CONF_LATITUDE]
        self._lon = entry.data[CONF_LONGITUDE]

    async def _async_update_data(self) -> dict[str, Reading | None]:
        try:
            data = await fetch_open_meteo(self._session, self._lat, self._lon)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Open-Meteo niet bereikbaar: {err}") from err
        return {
            key: Reading(data[key][1], data[key][0]) if key in data else None
            for key in QUANTITIES
        }
