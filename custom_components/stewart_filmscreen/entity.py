"""Base entity for Stewart Filmscreen."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_MANUFACTURER, ATTR_MODEL, DOMAIN
from .coordinator import StewartFilmscreenCoordinator


class StewartFilmscreenEntity(CoordinatorEntity[StewartFilmscreenCoordinator]):
    """Base coordinator entity with shared device metadata."""

    def __init__(
        self, coordinator: StewartFilmscreenCoordinator, unique_id: str
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.client.host)},
            manufacturer=ATTR_MANUFACTURER,
            model=ATTR_MODEL,
            name=f"{ATTR_MANUFACTURER} {ATTR_MODEL}",
        )
