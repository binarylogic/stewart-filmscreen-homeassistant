"""Test Stewart Filmscreen service registration helpers."""

from __future__ import annotations

from custom_components.stewart_filmscreen.const import (
    ATTR_PRESET_NUMBER,
    DOMAIN,
    SERVICE_RECALL_PRESET,
    SERVICE_STORE_PRESET,
)
from custom_components.stewart_filmscreen.services import (
    async_setup_services,
    async_unload_services,
)


async def test_services_setup_repairs_partial_registration(hass) -> None:
    """Test service setup re-registers whichever service is missing."""
    await async_setup_services(hass)
    hass.services.async_remove(DOMAIN, SERVICE_STORE_PRESET)

    await async_setup_services(hass)

    assert hass.services.has_service(DOMAIN, SERVICE_RECALL_PRESET)
    assert hass.services.has_service(DOMAIN, SERVICE_STORE_PRESET)

    async_unload_services(hass)


async def test_services_dispatch_to_registered_entries(
    hass, mock_config_entry, mock_setup_entry, mock_stewart_client
) -> None:
    """Test domain services call through to the client."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_RECALL_PRESET,
        {ATTR_PRESET_NUMBER: 2},
        blocking=True,
    )
    await hass.services.async_call(
        DOMAIN,
        SERVICE_STORE_PRESET,
        {ATTR_PRESET_NUMBER: 3},
        blocking=True,
    )

    mock_stewart_client.recall_preset.assert_awaited_once_with(2)
    mock_stewart_client.store_preset.assert_awaited_once_with(3)
