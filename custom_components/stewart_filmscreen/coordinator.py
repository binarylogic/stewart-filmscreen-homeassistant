"""Push coordinator for Stewart Filmscreen state."""

from __future__ import annotations

import contextlib
import logging
from copy import deepcopy

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from stewart_filmscreen.client import StewartFilmscreenClient
from stewart_filmscreen.models import ProtocolMessage

from .models import MotorState, StewartFilmscreenState


class StewartFilmscreenCoordinator(DataUpdateCoordinator[StewartFilmscreenState]):
    """Push coordinator backed by stewart_filmscreen client callbacks."""

    def __init__(self, hass: HomeAssistant, client: StewartFilmscreenClient) -> None:
        super().__init__(
            hass, logger=logging.getLogger(__name__), name="stewart_filmscreen"
        )
        self.client = client
        self._running = False
        self._state = StewartFilmscreenState()

    async def async_start(self, auth_timeout: float = 10.0) -> None:
        if self._running:
            return
        self._running = True
        self.client.register_callback(self._handle_message)
        await self.client.start()
        await self.client.wait_authenticated(timeout=auth_timeout)
        self._state.authenticated = True
        self.async_set_updated_data(self._snapshot())

    async def async_shutdown(self) -> None:
        if not self._running:
            return
        self.client.deregister_callback(self._handle_message)
        await self.client.stop_client()
        self._running = False

    async def _async_update_data(self) -> StewartFilmscreenState:
        return self._snapshot()

    def _snapshot(self) -> StewartFilmscreenState:
        return deepcopy(self._state)

    async def _handle_message(self, msg: ProtocolMessage) -> None:
        motor = self._state.motors.setdefault(msg.motor, MotorState())
        if msg.kind == "event" and msg.name == "POSITION" and msg.value is not None:
            with contextlib.suppress(ValueError):
                motor.position = int(round(float(msg.value)))
        if msg.kind == "event" and msg.name == "STATUS" and msg.value is not None:
            motor.status = msg.value
        self.async_set_updated_data(self._snapshot())
