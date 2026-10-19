"""Config flow voor Strand & Zee: kies een zwemlocatie uit een dropdown."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import load_spots
from .const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, CONF_SPOT, DOMAIN


class StrandEnZeeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        spots = await self.hass.async_add_executor_job(load_spots)
        by_label = {s["label"]: s for s in spots}

        if user_input is not None:
            spot = by_label[user_input[CONF_SPOT]]
            await self.async_set_unique_id(f"{spot['lat']:.4f}_{spot['lon']:.4f}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=spot["label"],
                data={
                    CONF_NAME: spot["label"],
                    CONF_LATITUDE: spot["lat"],
                    CONF_LONGITUDE: spot["lon"],
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_SPOT): SelectSelector(
                    SelectSelectorConfig(
                        options=list(by_label),
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
