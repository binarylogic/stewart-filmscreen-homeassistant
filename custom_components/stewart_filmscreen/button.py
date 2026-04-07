"""Button platform."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_PRESET_NUMBER, MIN_PRESET_NUMBER
from .entity import StewartFilmscreenEntity
from .models import StewartFilmscreenIntegrationData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data: StewartFilmscreenIntegrationData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        StewartFilmscreenPresetButton(data, preset_number)
        for preset_number in range(MIN_PRESET_NUMBER, MAX_PRESET_NUMBER + 1)
    )


class StewartFilmscreenPresetButton(StewartFilmscreenEntity, ButtonEntity):
    """Button entity that recalls a preset."""

    def __init__(
        self, data: StewartFilmscreenIntegrationData, preset_number: int
    ) -> None:
        super().__init__(
            data.coordinator,
            f"{data.coordinator.client.host}_recall_preset_{preset_number}",
        )
        self._client = data.client
        self._preset_number = preset_number
        self._attr_name = f"Recall Preset {preset_number}"

    @property
    def available(self) -> bool:
        return self._client.connected

    async def async_press(self) -> None:
        await self._client.recall_preset(self._preset_number)
