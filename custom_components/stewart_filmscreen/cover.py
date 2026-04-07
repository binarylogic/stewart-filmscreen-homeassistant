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
    STATUS_EXTENDING,
    STATUS_RETRACTING,
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
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
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
        return self._ha_position_from_motor_position(motor.position)

    @property
    def is_closed(self) -> bool | None:
        pos = self.current_cover_position
        if pos is None:
            return None
        return pos == 0

    @property
    def is_opening(self) -> bool | None:
        status = self._motor_status
        if status is None:
            return None
        if status == STATUS_RETRACTING:
            return not self._invert
        if status == STATUS_EXTENDING:
            return self._invert
        return False

    @property
    def is_closing(self) -> bool | None:
        status = self._motor_status
        if status is None:
            return None
        if status == STATUS_EXTENDING:
            return not self._invert
        if status == STATUS_RETRACTING:
            return self._invert
        return False

    async def async_open_cover(self, **kwargs) -> None:
        command = COMMAND_DOWN if self._invert else COMMAND_UP
        await self._client.send_command(self._motor, command)

    async def async_close_cover(self, **kwargs) -> None:
        command = COMMAND_UP if self._invert else COMMAND_DOWN
        await self._client.send_command(self._motor, command)

    async def async_stop_cover(self, **kwargs) -> None:
        await self._client.send_command(self._motor, COMMAND_STOP)

    @property
    def _motor_status(self) -> str | None:
        motor = self.coordinator.data.motors.get(self._motor)
        return None if motor is None else motor.status

    def _ha_position_from_motor_position(self, motor_position: int) -> int:
        bounded_position = max(0, min(100, motor_position))
        if self._invert:
            return bounded_position
        return 100 - bounded_position
