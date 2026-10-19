"""DataUpdateCoordinator voor Strand & Zee."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import fetch_latest, fetch_open_meteo, nearest_stations
from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_DISTANCE,
    CONF_SOURCE,
    DEFAULT_SOURCE,
    DOMAIN,
    MAX_CANDIDATES,
    SCAN_INTERVAL_MINUTES,
    SOURCE_OPEN_METEO,
)

_LOGGER = logging.getLogger(__name__)

# key -> (compartiment, grootheid)
QUANTITIES: dict[str, tuple[str, str]] = {
    "water_temperature": ("OW", "T"),
    "wave_height": ("OW", "Hm0"),
    "wave_period": ("OW", "Tm02"),
    "wind_speed": ("LT", "WINDSHD"),
    "wind_direction": ("LT", "WINDRTG"),
}


@dataclass
class Reading:
    """Eén meetwaarde met herkomst."""

    value: float
    timestamp: datetime
    station_code: str
    station_name: str
    distance_km: float


class StrandEnZeeCoordinator(DataUpdateCoordinator[dict[str, Reading | None]]):
    """Haalt per grootheid de nieuwste waarde van het dichtstbijzijnde live station."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, stations: list[dict[str, Any]]
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )
        self._stations = stations
        self._session = async_get_clientsession(hass)
        cfg = entry.data
        self._lat = cfg[CONF_LATITUDE]
        self._lon = cfg[CONF_LONGITUDE]
        self._max_km = cfg[CONF_MAX_DISTANCE]
        self.source = cfg.get(CONF_SOURCE, DEFAULT_SOURCE)

    def has_candidates(self, key: str) -> bool:
        """Bestaat er minstens één station in bereik voor deze grootheid?"""
        if self.source == SOURCE_OPEN_METEO:
            return True
        return bool(
            nearest_stations(self._stations, self._lat, self._lon, QUANTITIES[key][1], self._max_km)
        )

    async def _async_update_open_meteo(self) -> dict[str, Reading | None]:
        try:
            data = await fetch_open_meteo(self._session, self._lat, self._lon)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Open-Meteo niet bereikbaar: {err}") from err
        result: dict[str, Reading | None] = {}
        for key in QUANTITIES:
            item = data.get(key)
            result[key] = (
                Reading(item[1], item[0], "open-meteo", "Open-Meteo (model)", 0.0)
                if item
                else None
            )
        return result

    async def _async_update_data(self) -> dict[str, Reading | None]:
        if self.source == SOURCE_OPEN_METEO:
            return await self._async_update_open_meteo()
        result: dict[str, Reading | None] = {}
        errors = 0
        attempts = 0
        for key, (comp, grootheid) in QUANTITIES.items():
            candidates = nearest_stations(
                self._stations, self._lat, self._lon, grootheid, self._max_km
            )[:MAX_CANDIDATES]
            result[key] = None
            for dist, station in candidates:
                attempts += 1
                try:
                    latest = await fetch_latest(self._session, station["code"], comp, grootheid)
                except (aiohttp.ClientError, TimeoutError, ValueError) as err:
                    _LOGGER.debug("RWS-verzoek mislukt (%s/%s): %s", station["code"], grootheid, err)
                    errors += 1
                    continue
                if latest is None:
                    continue
                ts, value = latest
                if key == "wave_height":
                    value = value / 100  # cm -> m
                result[key] = Reading(value, ts, station["code"], station["name"], round(dist, 1))
                break
        if attempts and errors == attempts:
            raise UpdateFailed("Rijkswaterstaat WaterWebservices niet bereikbaar")
        return result
