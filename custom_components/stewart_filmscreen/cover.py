"""Cover platform."""

from __future__ import annotations

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from stewart_filmscreen.const import (
    COMMAND_DOWN,
    COMMAND_STOP,
    COMMAND_UP,
    MOTOR_A,
    MOTOR_B,
    MOTOR_C,
    MOTOR_D,
)

from .const import CONF_INVERT_A, CONF_INVERT_B, CONF_INVERT_C, CONF_INVERT_D, DOMAIN
from .entity import StewartFilmscreenEntity
from .models import StewartFilmscreenIntegrationData

MOTORS = [MOTOR_A, MOTOR_B, MOTOR_C, MOTOR_D]
INVERT_KEYS = {
    MOTOR_A: CONF_INVERT_A,
    MOTOR_B: CONF_INVERT_B,
    MOTOR_C: CONF_INVERT_C,
    MOTOR_D: CONF_INVERT_D,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data: StewartFilmscreenIntegrationData = hass.data[DOMAIN][entry.entry_id]

    entities: list[StewartFilmscreenCover] = []
    for motor in MOTORS:
        invert = bool(entry.options.get(INVERT_KEYS[motor], False))
        entities.append(StewartFilmscreenCover(data, motor, invert=invert))

    async_add_entities(entities)


class StewartFilmscreenCover(StewartFilmscreenEntity, CoverEntity):
    """Cover entity for a single CVM motor."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(
        self, data: StewartFilmscreenIntegrationData, motor: str, *, invert: bool
    ) -> None:
        super().__init__(data.coordinator, f"{data.coordinator.client.host}_{motor}")
        self._client = data.client
        self._motor = motor
        self._invert = invert
        self._attr_name = f"Screen Motor {motor.rsplit('.', 2)[1]}"

    @property
    def available(self) -> bool:
        return self._client.connected

    @property
    def current_cover_position(self) -> int | None:
        motor = self.coordinator.data.motors.get(self._motor)
        if motor is None or motor.position is None:
            return None
        # CVM reports percent extension, HA cover expects open percentage.
        return max(0, min(100, 100 - motor.position))

    @property
    def is_closed(self) -> bool | None:
        pos = self.current_cover_position
        if pos is None:
            return None
        return pos == 0

    async def async_set_cover_position(self, **kwargs) -> None:
        # CVM protocol has no direct absolute set position command in documented subset.
        # Keep deterministic behavior and rely on presets for absolute movements.
        target = kwargs.get("position")
        if target is None:
            return
        if int(target) <= 0:
            await self.async_close_cover()
        elif int(target) >= 100:
            await self.async_open_cover()

    async def async_open_cover(self, **kwargs) -> None:
        command = COMMAND_DOWN if self._invert else COMMAND_UP
        await self._client.send_command(self._motor, command)

    async def async_close_cover(self, **kwargs) -> None:
        command = COMMAND_UP if self._invert else COMMAND_DOWN
        await self._client.send_command(self._motor, command)

    async def async_stop_cover(self, **kwargs) -> None:
        await self._client.send_command(self._motor, COMMAND_STOP)
