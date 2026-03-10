"""Service registration helpers."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_PRESET_NUMBER,
    DOMAIN,
    SERVICE_RECALL_PRESET,
    SERVICE_STORE_PRESET,
)
from .models import StewartFilmscreenIntegrationData

SERVICE_SCHEMA = vol.Schema({vol.Required(ATTR_PRESET_NUMBER): cv.positive_int})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register domain services once."""

    async def _recall(call: ServiceCall) -> None:
        preset_number = int(call.data[ATTR_PRESET_NUMBER])
        for data in _integration_data(hass):
            await data.client.recall_preset(preset_number)

    async def _store(call: ServiceCall) -> None:
        preset_number = int(call.data[ATTR_PRESET_NUMBER])
        for data in _integration_data(hass):
            await data.client.store_preset(preset_number)

    if not hass.services.has_service(DOMAIN, SERVICE_RECALL_PRESET):
        hass.services.async_register(
            DOMAIN, SERVICE_RECALL_PRESET, _recall, schema=SERVICE_SCHEMA
        )
    if not hass.services.has_service(DOMAIN, SERVICE_STORE_PRESET):
        hass.services.async_register(
            DOMAIN, SERVICE_STORE_PRESET, _store, schema=SERVICE_SCHEMA
        )


def async_unload_services(hass: HomeAssistant) -> None:
    """Unload domain services."""
    hass.services.async_remove(DOMAIN, SERVICE_RECALL_PRESET)
    hass.services.async_remove(DOMAIN, SERVICE_STORE_PRESET)


def _integration_data(hass: HomeAssistant) -> list[StewartFilmscreenIntegrationData]:
    domain_data = hass.data.get(DOMAIN, {})
    return [
        v
        for v in domain_data.values()
        if isinstance(v, StewartFilmscreenIntegrationData)
    ]
