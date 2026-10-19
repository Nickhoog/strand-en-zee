"""Config flow voor Strand & Zee."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import load_stations, nearest_stations
from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_DISTANCE,
    CONF_NAME,
    CONF_SOURCE,
    DEFAULT_MAX_DISTANCE,
    DEFAULT_SOURCE,
    DOMAIN,
    SOURCE_OPEN_METEO,
    SOURCE_RWS,
)


class StrandEnZeeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            lat, lon = user_input[CONF_LATITUDE], user_input[CONF_LONGITUDE]
            max_km = user_input[CONF_MAX_DISTANCE]
            stations = await self.hass.async_add_executor_job(load_stations)
            in_range = user_input[CONF_SOURCE] == SOURCE_OPEN_METEO or any(
                nearest_stations(stations, lat, lon, g, max_km)
                for g in ("T", "Hm0", "WINDSHD")
            )
            if not in_range:
                errors["base"] = "no_stations"
            else:
                await self.async_set_unique_id(f"{user_input[CONF_SOURCE]}_{lat:.3f}_{lon:.3f}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        defaults = user_input or {}
        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "Strand")): str,
                vol.Required(
                    CONF_LATITUDE, default=defaults.get(CONF_LATITUDE, self.hass.config.latitude)
                ): vol.All(vol.Coerce(float), vol.Range(min=50, max=56)),
                vol.Required(
                    CONF_LONGITUDE, default=defaults.get(CONF_LONGITUDE, self.hass.config.longitude)
                ): vol.All(vol.Coerce(float), vol.Range(min=2, max=8)),
                vol.Required(
                    CONF_SOURCE, default=defaults.get(CONF_SOURCE, DEFAULT_SOURCE)
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[SOURCE_RWS, SOURCE_OPEN_METEO],
                        translation_key="source",
                        mode=SelectSelectorMode.LIST,
                    )
                ),
                vol.Required(
                    CONF_MAX_DISTANCE, default=defaults.get(CONF_MAX_DISTANCE, DEFAULT_MAX_DISTANCE)
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=150)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
