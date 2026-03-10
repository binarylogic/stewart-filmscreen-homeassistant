"""The Stewart Filmscreen integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import Event, HomeAssistant

from stewart_filmscreen.client import StewartFilmscreenClient

from .const import DOMAIN, PLATFORMS
from .coordinator import StewartFilmscreenCoordinator
from .models import StewartFilmscreenIntegrationData
from .services import async_setup_services, async_unload_services


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = StewartFilmscreenClient(
        host=str(entry.data[CONF_HOST]).strip(),
        port=int(entry.data[CONF_PORT]),
        username=str(entry.data[CONF_USERNAME]),
        password=str(entry.data[CONF_PASSWORD]),
    )
    coordinator = StewartFilmscreenCoordinator(hass, client)
    try:
        await coordinator.async_start()
    except Exception:
        await coordinator.async_shutdown()
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = StewartFilmscreenIntegrationData(
        client=client, coordinator=coordinator
    )
    await async_setup_services(hass)

    async def _shutdown(event: Event) -> None:
        await coordinator.async_shutdown()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _shutdown)
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data: StewartFilmscreenIntegrationData = hass.data[DOMAIN].pop(entry.entry_id)
        await data.coordinator.async_shutdown()
        if not hass.data[DOMAIN]:
            async_unload_services(hass)
            hass.data.pop(DOMAIN, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
