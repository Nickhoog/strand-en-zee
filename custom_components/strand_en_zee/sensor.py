"""Sensoren voor Strand & Zee."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTIONS, CONF_NAME, DOMAIN
from .coordinator import Reading, StrandEnZeeCoordinator

COMPASS = ["N", "NNO", "NO", "ONO", "O", "OZO", "ZO", "ZZO", "Z", "ZZW", "ZW", "WZW", "W", "WNW", "NW", "NNW"]

DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="wave_height",
        translation_key="wave_height",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        icon="mdi:waves",
    ),
    SensorEntityDescription(
        key="wave_period",
        translation_key="wave_period",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:sine-wave",
    ),
    SensorEntityDescription(
        key="wind_speed",
        translation_key="wind_speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:compass-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: StrandEnZeeCoordinator = entry.runtime_data
    async_add_entities(
        StrandEnZeeSensor(coordinator, entry, desc)
        for desc in DESCRIPTIONS
        if coordinator.has_candidates(desc.key)
    )


class StrandEnZeeSensor(CoordinatorEntity[StrandEnZeeCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: StrandEnZeeCoordinator, entry: ConfigEntry, description: SensorEntityDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_attribution = ATTRIBUTIONS[coordinator.source]
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data[CONF_NAME],
            manufacturer="Open-Meteo" if coordinator.source == "open_meteo" else "Rijkswaterstaat",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def _reading(self) -> Reading | None:
        return (self.coordinator.data or {}).get(self.entity_description.key)

    @property
    def available(self) -> bool:
        return super().available and self._reading is not None

    @property
    def native_value(self) -> float | None:
        return self._reading.value if self._reading else None

    @property
    def extra_state_attributes(self) -> dict[str, object] | None:
        r = self._reading
        if r is None:
            return None
        attrs: dict[str, object] = {
            "station": r.station_name,
            "station_code": r.station_code,
            "distance_km": r.distance_km,
            "measured_at": r.timestamp.isoformat(),
        }
        if self.entity_description.key == "wind_direction":
            attrs["compass"] = COMPASS[round(r.value / 22.5) % 16]
        return attrs
